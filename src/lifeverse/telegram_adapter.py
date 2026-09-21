from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramCommand:
    external_user_id: str
    text: str


class TelegramUpdateAdapter:
    def parse(self, update: dict) -> TelegramCommand:
        message = update.get("message") or update.get("edited_message")
        if not isinstance(message, dict):
            raise ValueError("unsupported telegram update")
        sender = message.get("from")
        text = message.get("text")
        if not isinstance(sender, dict) or "id" not in sender:
            raise ValueError("telegram sender missing")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("telegram text missing")
        return TelegramCommand(external_user_id=str(sender["id"]), text=text.strip())
