from jinja2 import Template
from promptflow import tool
from promptflow.connections import CustomConnection
from promptflow.contracts.types import PromptTemplate


@tool
def my_tool(connection: CustomConnection, prompt: PromptTemplate, **kwargs) -> str:
    return Template(
        prompt, trim_blocks=True, keep_trailing_newline=True
    ).render(**kwargs)
