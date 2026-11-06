# Navgold Custom01

A standalone Frappe app containing the **Amazon FBA Profit Calculator** for ERPNext.

The calculator is a Single DocType, so it behaves as one calculator rather than a list of saved records. It is GBP-only and does not read or write any ERPNext business data.

## Included

- Single DocType: `Amazon FBA Profit Calculator`
- FBA / Merchant fulfilment selector
- FBA fulfilment fee or merchant shipping cost
- Referral fee, FBA/merchant cost, inbound shipping, other costs
- Profit per unit, ROI, margin, total costs and breakeven sale price
- Target-margin sale price calculation
- Live client-side recalculation and server-side validation
- Unit tests for the calculations

## Install on a normal bench

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/harshid-lgtm/navgold_custom01 --branch main
bench --site your-site.local install-app navgold_custom01
bench --site your-site.local migrate
```

## Install on Frappe Cloud

1. Add this GitHub repository as an app in the Frappe Cloud bench group.
2. Deploy the bench.
3. Install `navgold_custom01` on the target site.
4. Run a site migration if it is not run automatically.

The calculator is then available at:

```text
/desk/navgold-custom/amazon-fba-profit-calculator
```

> This is a standalone test app. Do not install it alongside another app that
> already defines the same `Amazon FBA Profit Calculator` DocType — Frappe only
> allows one DocType with that name per site.

## License

MIT
