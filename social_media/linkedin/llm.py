from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.rate_limiters import InMemoryRateLimiter

# from langchain_groq import ChatGroq
from configuration import configuration
from pydantic import SecretStr

auth, _ = configuration()

# Initialize the model
# llm = ChatOllama(model="qwen2.5", num_ctx=32000)
llm = ChatGoogleGenerativeAI(
    model=auth["google"]["model"],
    api_key=SecretStr(auth["google"]["api_key"]),
    temperature=0.3,
    rate_limiter=InMemoryRateLimiter(
        requests_per_second=0.3,  # <-- Can only make a request once every 10 seconds!!
        check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
        max_bucket_size=5,  # Controls the maximum burst size.)
    ),
)
# llm = ChatGroq(model=auth["groq"]["model"], api_key=SecretStr(auth["groq"]["api_key"]))

# planner_llm = ChatOllama(model="qwen2.5", num_ctx=32000)
