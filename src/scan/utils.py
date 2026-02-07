from google.genai.types import HttpRetryOptions,HttpOptions

retry_options = HttpRetryOptions(
    attempts=3,
    initial_delay=1,
    exp_base=5
)
http_options = HttpOptions(retry_options=retry_options)