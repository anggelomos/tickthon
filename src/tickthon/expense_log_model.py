from attrs import define


@define
class ExpenseLog:
    """Represents a Ticktick task.

    Attributes:
        date: The title of the task, in format YYYY-MM-DD.
        expense: The amount of money spent.
        product: The product or service bought.
    """
    date: str
    expense: float
    product: str
