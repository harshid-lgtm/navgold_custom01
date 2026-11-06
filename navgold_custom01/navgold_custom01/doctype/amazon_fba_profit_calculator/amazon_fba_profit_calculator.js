// Copyright (c) 2026, developers@buildwithhussain.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Amazon FBA Profit Calculator', {
	refresh(frm) {
		frm.clear_custom_buttons();
		frm.add_custom_button(__('Reset example'), () => {
			frm.set_value({
				fulfilment_method: 'FBA',
				buy_price: 10,
				shipping_to_amazon: 0.5,
				other_costs: 0,
				sale_price: 25,
				referral_fee_pct: 15,
				fba_fulfilment_fee: 3.5,
				merchant_shipping_cost: 0,
				target_margin_pct: 30,
			});
			calculate(frm);
		});

		calculate(frm);
	},

	fulfilment_method: calculate,
	buy_price: calculate,
	shipping_to_amazon: calculate,
	other_costs: calculate,
	sale_price: calculate,
	referral_fee_pct: calculate,
	fba_fulfilment_fee: calculate,
	merchant_shipping_cost: calculate,
	target_margin_pct: calculate,
});

function calculate(frm) {
	const buyPrice = flt(frm.doc.buy_price);
	const shipping = flt(frm.doc.shipping_to_amazon);
	const otherCosts = flt(frm.doc.other_costs);
	const salePrice = flt(frm.doc.sale_price);
	const referralPct = flt(frm.doc.referral_fee_pct);
	const fulfilmentCost =
		frm.doc.fulfilment_method === 'Merchant'
			? flt(frm.doc.merchant_shipping_cost)
			: flt(frm.doc.fba_fulfilment_fee);
	const targetMarginPct = flt(frm.doc.target_margin_pct);
	const fixedCosts = buyPrice + fulfilmentCost + shipping + otherCosts;

	const referralFee = roundMoney((salePrice * referralPct) / 100);
	const totalCosts = roundMoney(
		referralFee + fulfilmentCost + buyPrice + shipping + otherCosts
	);
	const profit = roundMoney(salePrice - totalCosts);

	const roiBase = buyPrice + shipping + otherCosts;
	const roi = roiBase > 0 ? roundPercent((profit / roiBase) * 100) : null;
	const margin = salePrice > 0 ? roundPercent((profit / salePrice) * 100) : null;
	const breakeven =
		referralPct < 100 ? roundMoney(fixedCosts / (1 - referralPct / 100)) : null;

	// Margin = (S - S*r - fixed costs) / S, so S = fixed costs / (1 - r - margin).
	const targetMarginDenominator = 1 - referralPct / 100 - targetMarginPct / 100;
	const targetMarginSalePrice =
		targetMarginDenominator > 0
			? roundMoney(fixedCosts / targetMarginDenominator)
			: null;

	setIfChanged(frm, 'referral_fee', referralFee);
	setIfChanged(frm, 'total_costs', totalCosts);
	setIfChanged(frm, 'profit_per_unit', profit);
	setIfChanged(frm, 'roi', roi);
	setIfChanged(frm, 'margin', margin);
	setIfChanged(frm, 'breakeven_sale_price', breakeven);
	setIfChanged(frm, 'target_margin_sale_price', targetMarginSalePrice);

	const marginLabel = formatPercent(targetMarginPct);
	const targetDescription =
		targetMarginDenominator > 0
			? __(
					'Sale price needed to achieve the target margin, using the buy price, fulfilment cost, shipping and other costs above.'
			  )
			: __('Not achievable: target margin plus referral fee must be below 100%.');

	frm.set_df_property(
		'target_margin_sale_price',
		'label',
		__('Sale price if Margin {0}% (£)', [marginLabel])
	);
	frm.set_df_property('target_margin_sale_price', 'description', targetDescription);
}

function setIfChanged(frm, fieldname, value) {
	const current = frm.doc[fieldname];

	if (value === null) {
		if (current !== null && current !== undefined) {
			frm.set_value(fieldname, null);
		}
		return;
	}

	if (current === null || current === undefined || flt(current) !== flt(value)) {
		frm.set_value(fieldname, value);
	}
}

function roundMoney(value) {
	return Math.round((flt(value) + Number.EPSILON) * 100) / 100;
}

function roundPercent(value) {
	return Math.round((flt(value) + Number.EPSILON) * 10) / 10;
}

function formatPercent(value) {
	return String(Math.round((flt(value) + Number.EPSILON) * 100) / 100);
}
