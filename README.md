# AI Agent Workflow

## Team Information

**Workshop Team:** Group 1 & Group 7

**Team Members:**
- Ce Chen (9007166)
- Zhuoran Zhang (9048508)
- Haibo Yuan (9010929)
- Abdalla Mohamed (9089339)

**GitHub Repository:**  
https://github.com/chence/AI_Agent_Workshop.git

---

## Project Summary

This project focuses on building a simple civic-service AI agent workflow using a local public-service dataset.

The system was designed to answer user questions such as service ownership, routing responsibility, and next-step guidance.  
Instead of relying only on prompt responses, we combined retrieval, tool functions, verification logic, and evaluation methods.

Main workflow components include:

1. Knowledge base preparation and data cleaning  
2. Knowledge base expansion with additional services  
3. Tool layer for ownership lookup and routing  
4. Verification layer for grounded answers  
5. Retrieval layer for richer service information  
6. Evaluation using benchmark questions  
7. Metrics tracking and experiment outputs  
8. DVC pipeline ideas for reproducible workflows

---

## Key Results

- Built a structured AI agent workflow instead of a prompt-only solution  
- Added support for mixed and unclear civic requests  
- Compared baseline, retrieval, and tool-based methods  
- Demonstrated simple benchmark metrics and saved outputs  
- Improved answer grounding using official source links

---

## Roadblocks Faced

- Some dataset rows had missing fields such as source URLs  
- Ambiguous requests required hedging instead of direct answers  
- Matching user wording to service names needed normalization  
- Some outputs required extra verification for reliability

---

## Possible Missed Outcomes / Future Improvements

- Use semantic search embeddings instead of keyword matching  
- Add live website retrieval for updated service information  
- Expand the benchmark dataset with more realistic examples  
- Improve confidence scoring and ranking logic  
- Deploy as a web chatbot or civic assistant application

---

## Conclusion

This project helped us understand that successful AI systems depend not only on models, but also on good data, tool design, evaluation, and reproducible workflows.