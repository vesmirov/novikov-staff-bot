start:
	poetry run python bot.py

prepare:
	poetry run python prepare.py

schedule:
	poetry run python scheduler.py

day:
	poetry run python notifier.py -c day

day-law:
	poetry run python notifier.py -c day-law

day-sales:
	poetry run python notifier.py -c day-sales

week:
	poetry run python notifier.py -c week

week-law:
	poetry run python notifier.py -c week-law

week-sales:
	poetry run python notifier.py -c week-sales

kpi-first-notify:
	poetry run python notifier.py -c kpi-first

kpi-second-notify:
	poetry run python notifier.py -c kpi-second

plan-day-first-notify:
	poetry run python notifier.py -c plan-day-first

plan-day-second-notify:
	poetry run python notifier.py -c plan-day-second

plan-week-first-notify:
	poetry run python notifier.py -c plan-week-first

plan-week-second-notify:
	poetry run python notifier.py -c plan-week-second

plan-day-save-sales:
	poetry run python updater.py -c day-sales

plan-week-save-sales:
	poetry run python updater.py -c week-sales

plan-week-save-law:
	poetry run python updater.py -c week-law

lawsuits:
	poetry run python notifier.py -c lawsuits

lint:
	poetry run flake8
