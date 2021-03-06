from const import SDATE, DIR, CONFIG, logger
from datetime import datetime, timedelta
from traceback import format_exc
from socket import gethostname
from pathlib import Path
import sys, os

sys.path.append(f"{DIR}/..")
from utils import send_to_bucket, send_metric, save_items

if __name__ == '__main__':

	if gethostname() != CONFIG['MACHINE']['HOSTNAME']:
		CONFIG['GCP']['RAW_BUCKET'] = "tmp_items"
		CONFIG['GCP']['RAW_VAULT'] = "tmp_items_vault"

	try:

		path = Path(f"{DIR}/news_data")
		xz_file = Path(f"{DIR}/news_data_backup/{SDATE}.tar.xz")

		n_items, n_unique = save_items(path, SDATE)
		send_metric(CONFIG, "rss_count", "int64_value", n_items)
		send_metric(CONFIG, "unique_rss_count", "int64_value", n_unique)

		send_to_bucket(
			CONFIG['GCP']['RAW_BUCKET'],
			'rss',
			xz_file,
			logger=logger
		)

		send_to_bucket(
			CONFIG['GCP']['RAW_VAULT'],
			'rss',
			xz_file,
			logger=logger
		)

		logger.info(f"RSS save successeful.")
		send_metric(CONFIG, "rss_save_success_indicator", "int64_value", 1)

	except Exception as e:

		logger.warning(f"RSS save failed. {e}, {format_exc()}")
		send_metric(CONFIG, "rss_save_success_indicator", "int64_value", 0)
