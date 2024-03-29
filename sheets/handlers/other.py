import logging
from typing import Optional

from settings import settings
from sheets.tools import get_cell_value

logger = logging.getLogger(__name__)


def get_funds_statistics(full=False) -> dict[str, tuple[str, str]]:
    """TODO"""

    result = {}

    for fund_data in settings.config['other']['funds']['items'].values():
        if fund_data['statistics']['admin_only'] and not full:
            continue

        fund_actual = get_cell_value(
            table_id=settings.config['other']['funds']['google']['table'],
            sheet_id=settings.config['other']['funds']['google']['sheet'],
            cell=fund_data['statistics']['cells']['actual'],
        )
        fund_planned = get_cell_value(
            table_id=settings.config['other']['funds']['google']['table'],
            sheet_id=settings.config['other']['funds']['google']['sheet'],
            cell=fund_data['statistics']['cells']['planned'],
        )

        result[fund_data['name']] = (fund_actual, fund_planned)

    return result


# TODO use ENUM
def get_leader(period: str = 'today') -> Optional[list[str]]:
    """
    TODO

    Return value sample:
    [firstname_1 lastname_1, firstname_2 lastname_2]
    """

    result = []

    points_per_user: dict[str, Optional[int]] = {}
    for user_id, cells in settings.config['other']['leader']['candidates'].items():
        value = get_cell_value(
            table_id=settings.config['other']['leader']['google']['table'],
            sheet_id=settings.config['other']['leader']['google']['sheet'],
            # TODO fix this crunch during next refactoring
            cell=cells['today' if period == 'today' else 'yesterday']
        )

        try:
            points_per_user[user_id] = int(value)
        except ValueError:
            logger.error(
                'The retrieved points value of candidate is not numeric.',
                extra={'user_id': user_id, 'value': value},
            )
            points_per_user[user_id] = 0

    max_points = max(points_per_user.values())
    if max_points:
        for user_id, points in points_per_user.items():
            if points == max_points:
                result.append(
                    f'{settings.config["employees"][user_id]["firstname"]} '
                    f'{settings.config["employees"][user_id]["lastname"]}',
                )

    return result
