from aiogram.filters.callback_data import CallbackData


class SourceData(CallbackData, prefix="source"):
    source: str

class TargetData(CallbackData, prefix="target"):
    target: str
