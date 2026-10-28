I built a local-first AI Privacy & Compliance Gateway ("GuardRail AI") to solve a critical enterprise issue: accidental data leakage to cloud LLMs.

Instead of a generic API wrapper, I engineered a high-performance proxy microservice using FastAPI, Python, and SQLite. 

How it works:
1. Intercepts outgoing LLM prompt payloads locally.
2. Extracts and redacts PII using local Named-Entity Recognition (NER).
3. Vaults sensitive data structures dynamically, replacing them with tracking tokens.
4. Restores returning cloud AI responses seamlessly on the return network path.

Check out the architecture and full analytics dashboard in the video below! 

#AI #Cybersecurity #SoftwareEngineering #Python #FastAPI #MachineLearning