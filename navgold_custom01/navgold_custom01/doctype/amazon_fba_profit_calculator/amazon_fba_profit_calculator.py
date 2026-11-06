# Copyright (c) 2026, developers@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

MONEY_PRECISION = 2
PERCENT_PRECISION = 1


class AmazonFBAProfitCalculator(Document):
	"""A standalone FBA profit calculator. It never reads or writes ERPNext data."""

	def validate(self):
		# Keep the document self-contained and GBP-only, regardless of site defaults.
		self.currency = "GBP"
		if not self.fulfilment_method:
			self.fulfilment_method = "FBA"
		self.validate_inputs()
		self.calculate_totals()

	def validate_inputs(self):
		if self.fulfilment_method not in ("FBA", "Merchant"):
			frappe.throw(_("Fulfilment method must be FBA or Merchant."))

		for fieldname, label in (
			("buy_price", "Buy price"),
			("shipping_to_amazon", "Shipping to Amazon"),
			("other_costs", "Other costs"),
			("sale_price", "Sale price"),
			("referral_fee_pct", "Referral fee %"),
			("fba_fulfilment_fee", "FBA fulfilment fee"),
			("merchant_shipping_cost", "Shipping Cost"),
			("target_margin_pct", "Target margin %"),
		):
			if flt(self.get(fieldname)) < 0:
				frappe.throw(_("{0} cannot be negative.").format(_(label)))

		if flt(self.referral_fee_pct) > 100:
			frappe.throw(_("Referral fee % cannot be more than 100."))

	def calculate_totals(self):
		buy_price = flt(self.buy_price)
		shipping = flt(self.shipping_to_amazon)
		other_costs = flt(self.other_costs)
		sale_price = flt(self.sale_price)
		referral_pct = flt(self.referral_fee_pct)
		fulfilment_cost = (
			flt(self.merchant_shipping_cost)
			if self.fulfilment_method == "Merchant"
			else flt(self.fba_fulfilment_fee)
		)
		target_margin_pct = flt(self.target_margin_pct)
		fixed_costs = fulfilment_cost + buy_price + shipping + other_costs

		# Round the referral fee first so the stored cost breakdown adds up exactly.
		referral_fee = flt(sale_price * referral_pct / 100.0, MONEY_PRECISION)
		total_costs = flt(
			referral_fee + fulfilment_cost + buy_price + shipping + other_costs,
			MONEY_PRECISION,
		)
		profit = flt(sale_price - total_costs, MONEY_PRECISION)

		roi_base = buy_price + shipping + other_costs
		self.referral_fee = referral_fee
		self.total_costs = total_costs
		self.profit_per_unit = profit
		self.roi = (
			flt(profit / roi_base * 100.0, PERCENT_PRECISION)
			if roi_base > 0
			else None
		)
		self.margin = (
			flt(profit / sale_price * 100.0, PERCENT_PRECISION)
			if sale_price > 0
			else None
		)
		self.breakeven_sale_price = (
			flt(fixed_costs / (1 - referral_pct / 100.0), MONEY_PRECISION)
			if referral_pct < 100
			else None
		)

		# Margin = (S - S*r - fixed_costs) / S, so S = fixed_costs / (1 - r - margin).
		target_margin_denominator = (
			1 - referral_pct / 100.0 - target_margin_pct / 100.0
		)
		self.target_margin_sale_price = (
			flt(fixed_costs / target_margin_denominator, MONEY_PRECISION)
			if target_margin_denominator > 0
			else None
		)
