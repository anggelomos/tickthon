from attr import define
import attr


@define
class TicktickListIds:
    INBOX: str
    TODAY_BACKLOG: str
    WEEK_BACKLOG: str
    MONTH_BACKLOG: str
    WEIGHT_MEASUREMENTS: str

    def get_ids(self) -> list[str]:
        """Returns a list of all backlog values."""
        return [getattr(self, field.name) for field in attr.fields(self.__class__)]
