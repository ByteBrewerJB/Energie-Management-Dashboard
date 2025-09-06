from app.models.models import MonthlyMetric, Tariff

def calculate_financials(metric: MonthlyMetric, tariff: Tariff) -> dict:
    """
    Calculates financial values based on a MonthlyMetric record and an active Tariff.

    Args:
        metric: A MonthlyMetric object.
        tariff: A Tariff object.

    Returns:
        A dictionary with the calculated financial values.
    """
    import_costs_ex_vat = (metric.import_low_kwh * float(tariff.purchase_low_eur_kwh)) + \
                          (metric.import_high_kwh * float(tariff.purchase_high_eur_kwh))

    export_revenue_ex_vat = metric.export_total_kwh * float(tariff.sale_eur_kwh)

    net_monthly_result_ex_vat = export_revenue_ex_vat - import_costs_ex_vat

    vat_multiplier = 1 + float(tariff.vat_percentage)

    import_costs_inc_vat = import_costs_ex_vat * vat_multiplier
    export_revenue_inc_vat = export_revenue_ex_vat * vat_multiplier
    net_monthly_result_inc_vat = net_monthly_result_ex_vat * vat_multiplier

    return {
        "import_costs_ex_vat": import_costs_ex_vat,
        "export_revenue_ex_vat": export_revenue_ex_vat,
        "net_monthly_result_ex_vat": net_monthly_result_ex_vat,
        "import_costs_inc_vat": import_costs_inc_vat,
        "export_revenue_inc_vat": export_revenue_inc_vat,
        "net_monthly_result_inc_vat": net_monthly_result_inc_vat,
    }
