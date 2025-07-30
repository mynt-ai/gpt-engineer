from gpt_engineer.core.ai import AI, HumanMessage, SystemMessage

from gpt_engineer.applications.feature_cli.feature import Feature
from gpt_engineer.applications.feature_cli.repository import Repository
from gpt_engineer.applications.feature_cli.files import Files
from gpt_engineer.applications.feature_cli.file_selection import FileSelector
from gpt_engineer.applications.feature_cli.agents.agent_steps import (
    update_user_file_selection,
    confirm_chat_with_feature,
    get_git_context,
)
from gpt_engineer.applications.feature_cli.generation_tools import (
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

    def _get_chat_context(self):
        if self.feature.has_description():
            with_feature = confirm_chat_with_feature()

            if with_feature:
                file_selector = FileSelector(
                    self.project_path, self.repository, name="feature_files.yml"
                )

                update_user_file_selection(file_selector)
                selected_files = file_selector.get_from_yaml().included_files
                files = Files(self.project_path, selected_files)

                git_context = get_git_context(self.repository)

                context_string = build_files_context_string(
                    self.feature, git_context, files
                )

        if not context_string:
            update_user_file_selection(file_selector)
            selected_files = self.file_selector.get_from_yaml().included_files
            files = Files(self.project_path, selected_files)
            context_string = f"Files from code repository:\n\n{files.to_chat()}"

        return context_string

    def start(self):
        context_string = self._get_chat_context()

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
