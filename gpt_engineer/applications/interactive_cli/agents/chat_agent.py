from gpt_engineer.core.ai import AI, HumanMessage, SystemMessage

from gpt_engineer.applications.interactive_cli_loop.feature import Feature
from gpt_engineer.applications.interactive_cli_loop.repository import Repository
from gpt_engineer.applications.interactive_cli_loop.files import Files
from gpt_engineer.applications.interactive_cli_loop.file_selection import FileSelector
from gpt_engineer.applications.interactive_cli_loop.agents.agent_steps import (
    update_user_file_selection,
)
from gpt_engineer.applications.interactive_cli_loop.generation_tools import (
    build_files_context_string,
)


class ChatAgent:

    def __init__(
        self,
        ai: AI,
        project_path: str,
        feature: Feature,
        repository: Repository,
        file_selector: FileSelector,
    ):
        self.ai = ai
        self.project_path = project_path
        self.feature = feature
        self.repository = repository
        self.file_selector = file_selector

    def start(self):

        update_user_file_selection(self.file_selector)

        selected_files = self.file_selector.get_from_yaml().included_files

        files = Files(self.project_path, selected_files)

        context_string = build_files_context_string(
            self.feature, self.repository.get_git_context(), files
        )

        system = f"""You are the chat function of an AI software engineering tool called gpt engineer.
        
The tool takes a feature descriptioin, progress on the feature, git context, and repository files relevent to the feature 
and based on that it suggests new tasks to complete in order to progress the feature, and it implements those tasks for the user.

You are not that tool, you are the chat function of that tool. You are here to help the user discuss their code and their feature and understand discuss any part of it with you - a software engineering expert.

Always provide advice as to best software engineering practices.

Here is the context for your conversation: 

{context_string}"""

        messages = [
            SystemMessage(content=system),
            HumanMessage(content="Hi"),
        ]

        while True:
            print("\nAI:")
            response = self.ai.backoff_inference(messages)
            messages.append(response)

            print("\n\nYou:")
            user_message = input()
            messages.append(HumanMessage(content=user_message))
