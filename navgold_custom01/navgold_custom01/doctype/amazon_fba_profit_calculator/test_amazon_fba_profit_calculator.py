# Copyright (c) 2026, developers@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import UnitTestCase

DOCTYPE = "Amazon FBA Profit Calculator"


class TestAmazonFBAProfitCalculator(UnitTestCase):
	def build(self, **overrides):
		doc = frappe.new_doc(DOCTYPE)
		doc.update(
			{
				"fulfilment_method": "FBA",
				"buy_price": 10,
				"shipping_to_amazon": 0.5,
				"other_costs": 0,
				"sale_price": 25,
				"referral_fee_pct": 15,
				"fba_fulfilment_fee": 3.5,
				"merchant_shipping_cost": 0,
				"target_margin_pct": 30,
			}
		)
		doc.update(overrides)
		doc.calculate_totals()
		return doc

	def test_reference_example(self):
		doc = self.build()

		self.assertEqual(doc.referral_fee, 3.75)
		self.assertEqual(doc.total_costs, 17.75)
		self.assertEqual(doc.profit_per_unit, 7.25)
		self.assertEqual(doc.roi, 69.0)
		self.assertEqual(doc.margin, 29.0)
		self.assertEqual(doc.breakeven_sale_price, 16.47)
		self.assertEqual(doc.target_margin_sale_price, 25.45)

	def test_merchant_uses_shipping_cost_instead_of_fba_fee(self):
		doc = self.build(
			fulfilment_method="Merchant",
			merchant_shipping_cost=4.0,
			fba_fulfilment_fee=99,
		)

		self.assertEqual(doc.total_costs, 18.25)
		self.assertEqual(doc.profit_per_unit, 6.75)
		self.assertEqual(doc.target_margin_sale_price, 26.36)

	def test_fba_ignores_merchant_shipping_cost(self):
		doc = self.build(
			fulfilment_method="FBA",
			merchant_shipping_cost=99,
		)

		self.assertEqual(doc.total_costs, 17.75)
		self.assertEqual(doc.profit_per_unit, 7.25)

	def test_unknown_fulfilment_method_is_rejected(self):
		doc = self.build(fulfilment_method="Other")

		with self.assertRaises(frappe.ValidationError):
			doc.validate()

	def test_target_margin_sale_price(self):
		doc = self.build()

		self.assertEqual(doc.target_margin_sale_price, 25.45)

	def test_zero_target_margin_matches_breakeven(self):
		doc = self.build(target_margin_pct=0)

		self.assertEqual(doc.target_margin_sale_price, doc.breakeven_sale_price)

	def test_impossible_target_margin_returns_none(self):
		doc = self.build(target_margin_pct=90)

		self.assertIsNone(doc.target_margin_sale_price)

	def test_zero_cost_base_leaves_roi_undefined(self):
		doc = self.build(buy_price=0, shipping_to_amazon=0, other_costs=0)

		self.assertIsNone(doc.roi)
		self.assertIsNotNone(doc.profit_per_unit)

	def test_full_referral_fee_leaves_breakeven_undefined(self):
		doc = self.build(referral_fee_pct=100)

		self.assertIsNone(doc.breakeven_sale_price)

	def test_negative_input_is_rejected(self):
		doc = self.build(buy_price=-1)

		with self.assertRaises(frappe.ValidationError):
			doc.validate()

	def test_referral_fee_above_100_is_rejected(self):
		doc = self.build(referral_fee_pct=101)

		with self.assertRaises(frappe.ValidationError):
			doc.validate()
