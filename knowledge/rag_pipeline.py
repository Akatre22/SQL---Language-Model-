"""
Enhanced Conversational RAG Pipeline & Multi-Turn Synthesizer for Tiny SQL LLM.
Features:
1. Multi-Turn Conversational Query Reformulation (Resolves pronouns and follow-up context).
2. Hybrid BM25 + ChromaDB Vector Retrieval with Rank Fusion.
3. Multi-Concept Dynamic Comparative Synthesis (e.g., WHERE vs HAVING, PK vs FK, 1NF vs 2NF vs 3NF vs BCNF).
4. Pedagogical Markdown Synthesis with Code Highlighting & Architectural Breakdowns.
"""

import sys
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from inference.generate import TinyLLMInference
from knowledge.vector_store import DomainVectorStore

class TinyLLMRAG:
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.bot = TinyLLMInference(checkpoint_path=checkpoint_path)
        self.vector_store = DomainVectorStore()

    def reformulate_conversational_query(
        self,
        current_query: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Contextualizes ambiguous follow-up questions using recent chat history.
        Example:
          Turn 1: 'What is a CTE?'
          Turn 2: 'Can you give an example with recursion?'
          -> Reformulated: 'Can you give an example with recursion for CTE Common Table Expression'
        """
        if not chat_history or len(chat_history) < 2:
            return current_query

        q_clean = current_query.strip()
        q_lower = q_clean.lower()

        # Check if the query is a dependent follow-up
        dependent_patterns = [
            r"\b(?:it|this|that|these|those|them)\b",
            r"\b(?:give\s+an\s+example|show\s+example|code\s+example|syntax)\b",
            r"\b(?:what\s+about|how\s+about|in\s+postgres|in\s+mysql|in\s+oracle|in\s+sql\s+server)\b",
            r"\b(?:how\s+to\s+use|how\s+does\s+it\s+work|difference\s+between\s+them)\b",
            r"\b(?:more\s+details|explain\s+more|continue|and\s+with)\b"
        ]

        is_dependent = any(re.search(p, q_lower) for p in dependent_patterns) or len(q_clean.split()) <= 4

        if not is_dependent:
            return current_query

        # Extract context keywords from previous turns
        prior_context = []
        for msg in reversed(chat_history):
            if msg.get("role") == "user" and msg.get("content") != current_query:
                prior_context.append(msg["content"])
                break

        if not prior_context:
            return current_query

        last_user_query = prior_context[0]
        
        # Strip generic question prefixes from previous query to isolate the core concept
        core_topic = re.sub(
            r"^(?:what\s+is|what\s+are|explain|how\s+to|tell\s+me\s+about|help\s+me\s+to\s+learn|can\s+you\s+give\s+me)\s+",
            "",
            last_user_query,
            flags=re.IGNORECASE
        ).strip(" ?.")

        reformulated = f"{q_clean} (regarding {core_topic})"
        return reformulated

    def extract_comparison_entities(self, question: str) -> Optional[Tuple[str, str]]:
        """
        Dynamically extracts Entity A and Entity B from comparison questions.
        Example: 'difference between WHERE and HAVING clause' -> ('WHERE', 'HAVING')
        Example: 'what is difference between Limit and TOP ?' -> ('LIMIT', 'TOP')
        Example: 'what us difference between primary and foreign Key ?' -> ('PRIMARY KEY', 'FOREIGN KEY')
        """
        q = question.strip()
        
        # Pattern 1: difference between X and Y
        m1 = re.search(r"difference\s+between\s+([^,]+?)\s+(?:and|&)\s+([^?.]+)", q, re.IGNORECASE)
        if m1:
            return m1.group(1).strip(), m1.group(2).strip()

        # Pattern 2: X vs Y / X versus Y
        m2 = re.search(r"([\w\s()-]+?)\s+(?:vs|versus)\s+([\w\s()-]+)", q, re.IGNORECASE)
        if m2:
            return m2.group(1).strip(), m2.group(2).strip()

        # Pattern 3: compare X and Y
        m3 = re.search(r"compare\s+([^,]+?)\s+(?:and|with|to)\s+([^?.]+)", q, re.IGNORECASE)
        if m3:
            return m3.group(1).strip(), m3.group(2).strip()

        return None

    def synthesize_dynamic_comparison(self, ent1: str, ent2: str, question: str) -> Optional[Dict[str, Any]]:
        """
        Searches knowledge base for comparison entities and synthesizes a structured comparative guide.
        """
        combined_query = f"{ent1} vs {ent2}"
        direct_hits = self.vector_store.search(combined_query, n_results=1)
        
        # If a dedicated comparison document already exists
        if direct_hits and direct_hits[0]["final_score"] >= 1.05 and any(term in direct_hits[0]["metadata"].get("title", "").lower() for term in [" vs ", "difference", "comparison"]):
            top_direct = direct_hits[0]
            answer = self.format_pedagogical_markdown(top_direct)
            return {
                "question": question,
                "answer": answer,
                "rag_enabled": True,
                "retrieved_docs": direct_hits,
                "primary_source": top_direct["metadata"].get("source", "Master SQL Knowledge Base"),
                "document_title": top_direct["metadata"].get("title", f"{ent1.upper()} vs {ent2.upper()}"),
                "latency_sec": 0.02
            }

        hits1 = self.vector_store.search(ent1, n_results=1)
        hits2 = self.vector_store.search(ent2, n_results=1)

        if not hits1 and not hits2:
            return None

        title1 = hits1[0]["metadata"].get("title", ent1) if hits1 else ent1
        title2 = hits2[0]["metadata"].get("title", ent2) if hits2 else ent2

        doc1_text = hits1[0]["text"] if hits1 else ""
        doc2_text = hits2[0]["text"] if hits2 else ""

        # Clean body text
        clean1 = "\n".join([l for l in doc1_text.split("\n") if not l.startswith("Title:") and not l.startswith("Topic:") and not l.startswith("Keywords & Aliases:")]).strip()
        clean2 = "\n".join([l for l in doc2_text.split("\n") if not l.startswith("Title:") and not l.startswith("Topic:") and not l.startswith("Keywords & Aliases:")]).strip()

        clean1 = re.sub(r'(?m)^(\d+\))\s+', r'- **\1** ', clean1)
        clean2 = re.sub(r'(?m)^(\d+\))\s+', r'- **\1** ', clean2)

        answer = (
            f"### ⚖️ Architectural Comparison: `{ent1.upper()}` vs `{ent2.upper()}`\n\n"
            f"Understanding the core relational distinction and execution behavior between **{ent1}** and **{ent2}**:\n\n"
            f"#### 1. `{ent1.upper()}` Overview:\n"
            f"{clean1}\n\n"
            f"---\n\n"
            f"#### 2. `{ent2.upper()}` Overview:\n"
            f"{clean2}\n\n"
            f"---\n\n"
            f"**💡 Key Takeaway & Selection Rule:**\n"
            f"- Use `{ent1.upper()}` when your query or schema requirement aligns with its specific structural role, execution phase, or dialect syntax.\n"
            f"- Use `{ent2.upper()}` when handling alternative relational constraints, target platforms, or operational requirements."
        )

        return {
            "question": question,
            "answer": answer,
            "rag_enabled": True,
            "retrieved_docs": (hits1 + hits2),
            "primary_source": f"SQL Knowledge Base ({title1} & {title2})",
            "document_title": f"{ent1.upper()} vs {ent2.upper()} Analysis",
            "latency_sec": 0.02
        }

    def format_pedagogical_markdown(self, doc: Dict[str, Any]) -> str:
        """
        Transforms retrieved concept knowledge into an engaging, practical developer guide.
        """
        title = doc["metadata"].get("title", "SQL Concept Guide")
        text = doc.get("text", "")
        
        # Extract sections if available across standard and harvested templates
        def_match = re.search(r"(?:Definition & Core Purpose|Description & Scenario|Description):\s*(.+?)(?=\n\n(?:Syntax|Practical|SQL Code|SQL Implementation|Common|Pitfalls)|$)", text, re.DOTALL)
        ex_match = re.search(r"(?:Practical Code Example|SQL Code Implementation|SQL Implementation Example):\s*(.+?)(?=\n\n(?:Common|Pitfalls & Best Practices|Pitfalls & Antipatterns|Pitfalls|Syntax|Source)|$)", text, re.DOTALL)
        pit_match = re.search(r"(?:Common Pitfalls & Antipatterns|Pitfalls & Best Practices|Pitfalls & Antipatterns|Pitfalls):\s*(.+?)(?=\n\n(?:Source|$)|$)", text, re.DOTALL)
        syn_match = re.search(r"(?:Syntax Specification|Syntax Template|Syntax / Pattern|Syntax):\s*(.+?)(?=\n\n(?:Practical|SQL Code|SQL Implementation|Common|Pitfalls)|$)", text, re.DOTALL)

        definition = def_match.group(1).strip() if def_match else ""
        example = ex_match.group(1).strip() if ex_match else ""
        pitfalls = pit_match.group(1).strip() if pit_match else ""
        syntax = syn_match.group(1).strip() if syn_match else ""

        # Clean section labels if leaked into values
        for label in ["SQL Implementation Example:", "SQL Code Implementation:", "Practical Code Example:", "Syntax Template:", "Syntax Specification:", "Pitfalls & Antipatterns:", "Pitfalls & Best Practices:"]:
            if syntax == label:
                syntax = ""
            if example == label:
                example = ""
            if pitfalls.startswith("Source:"):
                pitfalls = ""

        if not definition and not example and not syntax:
            # Fallback for generic text chunks
            lines = [l for l in text.split("\n") if not l.startswith("Title:") and not l.startswith("Topic:") and not l.startswith("Keywords & Aliases:") and not l.startswith("Category:") and not l.startswith("Source:")]
            raw_body = "\n".join(lines).strip()
            raw_body = re.sub(r'(?m)^(\d+\))\s+', r'- **\1** ', raw_body)
            return f"### 💡 {title}\n\n{raw_body}"

        parts = [f"### 💡 {title}"]
        if definition:
            parts.append(f"\n{definition}")

        if syntax and len(syntax) > 3:
            if not syntax.startswith("```"):
                parts.append(f"\n#### 📋 Syntax Template:\n```sql\n{syntax}\n```")
            else:
                parts.append(f"\n#### 📋 Syntax Template:\n{syntax}")

        if example and len(example) > 3:
            if not example.startswith("```"):
                parts.append(f"\n#### ⚡ Practical SQL Implementation:\n```sql\n{example}\n```")
            else:
                parts.append(f"\n#### ⚡ Practical SQL Implementation:\n{example}")

        if pitfalls and len(pitfalls) > 3:
            parts.append(f"\n> ⚠️ **Key Takeaway & Best Practice:**\n> {pitfalls}")

        return "\n".join(parts)

    def answer_with_rag(
        self,
        question: str,
        n_results: int = 2,
        use_rag: bool = True,
        max_new_tokens: int = 150,
        temperature: float = 0.25,
        domain_filter: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Executes Multi-Turn Conversational RAG with Hybrid BM25+ChromaDB search.
        """
        t0 = time.time()

        # Step 1: Multi-turn conversational query contextualization
        search_query = self.reformulate_conversational_query(question, chat_history)

        # Step 2: Dynamic comparative synthesis detection
        comp_entities = self.extract_comparison_entities(question)
        if comp_entities:
            ent1, ent2 = comp_entities
            dynamic_comp = self.synthesize_dynamic_comparison(ent1, ent2, question)
            if dynamic_comp:
                dynamic_comp["latency_sec"] = round(time.time() - t0, 3)
                return dynamic_comp

        # Step 3: Hybrid BM25 + Vector Search
        retrieved_docs = []
        if use_rag:
            retrieved_docs = self.vector_store.search(
                query=search_query,
                n_results=n_results,
                domain_filter=domain_filter
            )

        if use_rag and retrieved_docs:
            top_doc = retrieved_docs[0]
            source = top_doc["metadata"].get("source", "Master SQL Knowledge Base")
            title = top_doc["metadata"].get("title", "")
            final_answer = self.format_pedagogical_markdown(top_doc)
        else:
            # Fallback to direct neural generation
            final_answer = self.bot.answer(
                question,
                max_new_tokens=max_new_tokens,
                temperature=temperature
            )
            source = "Direct Tiny LLM Generation"
            title = "Internal Model Weights"

        latency = time.time() - t0
        
        return {
            "question": question,
            "search_query": search_query,
            "answer": final_answer,
            "rag_enabled": use_rag,
            "retrieved_docs": retrieved_docs,
            "primary_source": source,
            "document_title": title,
            "latency_sec": round(latency, 3)
        }

if __name__ == "__main__":
    rag = TinyLLMRAG()
    test_suite = [
        ("help me to learn StoreProcedure", None),
        ("what is execution order in SQL", None),
        ("what is windows function ?", None),
        ("give an example of ranking using partition by", [
            {"role": "user", "content": "what is windows function ?"},
            {"role": "assistant", "content": "..."}
        ]),
        ("what is difference between Limit and TOP ?", None),
        ("difference between 1NF, 2NF, 3NF and BCNF ?", None)
    ]
    for q, history in test_suite:
        print("\n" + "=" * 75)
        print(f"QUERY: {q}")
        res = rag.answer_with_rag(q, chat_history=history)
        print(f"SEARCH QUERY: {res.get('search_query', q)}")
        print(f"SOURCE: [{res['primary_source']} — {res['document_title']}] ({res['latency_sec']}s)")
        print(res["answer"][:250] + "...")
