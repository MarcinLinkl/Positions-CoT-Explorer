reports_tables = {
    "report_legacy_futures_only": "report_legacy",
    "report_legacy_combined": "report_legacy",
    "report_disaggregated_futures_only": "report_disaggregated",
    "report_disaggregated_combined": "report_disaggregated",
    "report_tff_futures_only": "report_tff",
    "report_tff_combined": "report_tff",
    "report_suplemental_cit": "report_suplemental_cit",
}


positions_by_report = {
    "report_legacy": {
        "comm_positions": "Commercial",
        "noncomm_positions": "Non-Commercial",
        "nonrept_positions": "Non-Reportable",
        "tot_rept_positions": "Total Reportable",
    },
    "report_disaggregated": {
        "prod_merc_positions": "Producer/Merchant",
        "swap_positions": "Swap",
        "m_money_positions": "Managed Money",
        "other_rept_positions": "Other Reportable",
        "tot_rept_positions": "Total Reportable",
        "nonrept_positions": "Non-Reportable",
    },
    "report_tff": {
        "dealer_positions_all": "Dealer",
        "asset_mgr_positions": "Asset Manager",
        "lev_money_positions": "Leveraged Money",
        "other_rept_positions": "Other Reportable",
        "tot_rept_positions_all": "Total Reportable",
        "nonrept_positions_all": "Non-Reportable",
    },
    "report_suplemental_cit": {
        "NComm_Postions_All_NoCIT": "Non-Commercial - No CIT",
        "comm_positions_all_nocit": "Commercial - No CIT",
        "tot_rept_positions_all": "Total Reportable",
        "nonrept_positions_all": "Non-Reportable",
        "cit_positions_all": "CIT",
    },
}

reports_cols = {
    "report_legacy": {
        "positions": {
            "noncomm_positions_long_all": "Non-Commercial Positions Long All",
            "noncomm_positions_short_all": "Non-Commercial Positions Short All",
            "comm_positions_long_all": "Commercial Positions Long All",
            "comm_positions_short_all": "Commercial Positions Short All",
            "tot_rept_positions_long_all": "Total Report Positions Long All",
            "tot_rept_positions_short": "Total Report Positions Short",
            "nonrept_positions_long_all": "Non-Rept Positions Long All",
            "nonrept_positions_short_all": "Non-Rept Positions Short All",
        },
        "percentages": {
            "pct_of_oi_noncomm_long_all": "Percentage of Open Interest (Non-Commercial Long All)",
            "pct_of_oi_noncomm_short_all": "Percentage of Open Interest (Non-Commercial Short All)",
            "pct_of_oi_comm_long_all": "Percentage of Open Interest (Commercial Long All)",
            "pct_of_oi_comm_short_all": "Percentage of Open Interest (Commercial Short All)",
            "pct_of_oi_tot_rept_long_all": "Percentage of Open Interest (Total Report Long All)",
            "pct_of_oi_tot_rept_short": "Percentage of Open Interest (Total Report Short)",
            "pct_of_oi_nonrept_long_all": "Percentage of Open Interest (Non-Rept Long All)",
            "pct_of_oi_nonrept_short_all": "Percentage of Open Interest (Non-Rept Short All)",
        },
        "traders": {
            "traders_noncomm_long_all": "Traders Non-Commercial Long All",
            "traders_noncomm_short_all": "Traders Non-Commercial Short All",
            "traders_comm_long_all": "Traders Commercial Long All",
            "traders_comm_short_all": "Traders Commercial Short All",
            "traders_tot_rept_short_all": "Traders Total Report Short All",
            "traders_tot_rept_long_all": "Traders Total Report Long All",
        },
        "concentration": {
            "conc_gross_le_4_tdr_long": "Concentration Gross Le 4 Tdr Long",
            "conc_gross_le_4_tdr_short": "Concentration Gross Le 4 Tdr Short",
            "conc_gross_le_8_tdr_long": "Concentration Gross Le 8 Tdr Long",
            "conc_gross_le_8_tdr_short": "Concentration Gross Le 8 Tdr Short",
            "conc_net_le_4_tdr_long_all": "Concentration Net Le 4 Tdr Long All",
            "conc_net_le_4_tdr_short_all": "Concentration Net Le 4 Tdr Short All",
            "conc_net_le_8_tdr_long_all": "Concentration Net Le 8 Tdr Long All",
            "conc_net_le_8_tdr_short_all": "Concentration Net Le 8 Tdr Short All",
        },
    },
    "report_supplemental_cit": {
        "positions": {
            "NComm_Postions_Long_All_NoCIT": "Non-Commercial Positions Long All No CIT",
            "NComm_Postions_Short_All_NoCIT": "Non-Commercial Positions Short All No CIT",
            "comm_positions_long_all_nocit": "Commercial Positions Long All No CIT",
            "Comm_Positions_Short_All_NoCIT": "Commercial Positions Short All No CIT",
            "tot_rept_positions_long_all": "Total Reportable Positions Long All",
            "tot_rept_positions_short": "Total Reportable Positions Short",
            "nonrept_positions_long_all": "Non-Reportable Positions Long All",
            "nonrept_positions_short_all": "Non-Reportable Positions Short All",
            "cit_positions_long_all": "CIT Positions Long All",
            "cit_positions_short_all": "CIT Positions Short All",
        },
        "percentages": {
            "pct_oi_noncomm_long_all_nocit": "Percentage of Open Interest in Non-Commercial Long Positions All No CIT",
            "Pct_OI_NonComm_Short_All_NoCIT": "Percentage of Open Interest in Non-Commercial Short Positions All No CIT",
            "pct_oi_comm_long_all_nocit": "Percentage of Open Interest in Commercial Long Positions All No CIT",
            "pct_oi_comm_short_all_nocit": "Percentage of Open Interest in Commercial Short Positions All No CIT",
            "Pct_OI_Tot_Rept_Long_All_NoCIT": "Percentage of Open Interest in Total Reportable Long Positions All No CIT",
            "Pct_OI_Tot_Rept_Short_All_NoCIT": "Percentage of Open Interest in Total Reportable Short Positions All No CIT",
            "pct_oi_nonrept_long_all_nocit": "Percentage of Open Interest in Non-Reportable Long Positions All No CIT",
            "Pct_OI_NonRept_Short_All_NoCIT": "Percentage of Open Interest in Non-Reportable Short Positions All No CIT",
            "pct_oi_cit_long_all": "Percentage of Open Interest in CIT Long Positions All",
            "pct_oi_cit_short_all": "Percentage of Open Interest in CIT Short Positions All",
        },
        "traders": {
            "Traders_NonComm_Long_All_NoCIT": "Number of Traders with Non-Commercial Long Positions All No CIT",
            "Traders_NonComm_Short_All_NoCIT": "Number of Traders with Non-Commercial Short Positions All No CIT",
            "traders_comm_long_all_nocit": "Number of Traders with Commercial Long Positions All No CIT",
            "traders_comm_short_all_nocit": "Number of Traders with Commercial Short Positions All No CIT",
            "Traders_Tot_Rept_Long_All_NoCIT": "Number of Traders with Total Reportable Long Positions All No CIT",
            "Traders_Tot_Rept_Short_All_NoCIT": "Number of Traders with Total Reportable Short Positions All No CIT",
            "traders_cit_long_all": "Number of Traders with CIT Long Positions All",
            "traders_cit_short_all": "Number of Traders with CIT Short Positions All",
        },
    },
    "report_disaggregated": {
        "positions": {
            "prod_merc_positions_long": "Producer/Merchant Positions Long",
            "prod_merc_positions_short": "Producer/Merchant Positions Short",
            "swap_positions_long_all": "Swap Positions Long All",
            "swap__positions_short_all": "Swap Positions Short All",
            "m_money_positions_long_all": "Managed Money Positions Long All",
            "m_money_positions_short_all": "Managed Money Positions Short All",
            "other_rept_positions_long": "Other Reportable Positions Long",
            "other_rept_positions_short": "Other Reportable Positions Short",
            "tot_rept_positions_long_all": "Total Report Positions Long All",
            "tot_rept_positions_short": "Total Report Positions Short",
            "nonrept_positions_long_all": "Non-Reportable Positions Long All",
            "nonrept_positions_short_all": "Non-Reportable Positions Short All",
        },
        "percentages": {
            "pct_of_oi_prod_merc_long": "Percentage of Open Interest (Producer/Merchant Long)",
            "pct_of_oi_prod_merc_short": "Percentage of Open Interest (Producer/Merchant Short)",
            "pct_of_oi_swap_long_all": "Percentage of Open Interest (Swap Long All)",
            "pct_of_oi_swap_short_all": "Percentage of Open Interest (Swap Short All)",
            "pct_of_oi_m_money_long_all": "Percentage of Open Interest (Managed Money Long All)",
            "pct_of_oi_m_money_short_all": "Percentage of Open Interest (Managed Money Short All)",
            "pct_of_oi_other_rept_long": "Percentage of Open Interest (Other Reportable Long)",
            "pct_of_oi_other_rept_short": "Percentage of Open Interest (Other Reportable Short)",
            "pct_of_oi_tot_rept_long_all": "Percentage of Open Interest (Total Report Long All)",
            "pct_of_oi_tot_rept_short": "Percentage of Open Interest (Total Report Short)",
            "pct_of_oi_nonrept_long_all": "Percentage of Open Interest (Non-Reportable Long All)",
            "pct_of_oi_nonrept_short_all": "Percentage of Open Interest (Non-Reportable Short All)",
        },
        "traders": {
            "traders_prod_merc_long_all": "Traders Producer/Merchant Long All",
            "traders_prod_merc_short_all": "Traders Producer/Merchant Short All",
            "traders_swap_long_all": "Traders Swap Long All",
            "traders_swap_short_all": "Traders Swap Short All",
            "traders_m_money_long_all": "Traders Managed Money Long All",
            "traders_m_money_short_all": "Traders Managed Money Short All",
            "traders_other_rept_long_all": "Traders Other Reportable Long All",
            "traders_other_rept_short": "Traders Other Reportable Short",
            "traders_tot_rept_long_all": "Traders Total Report Long All",
            "traders_tot_rept_short_all": "Traders Total Report Short All",
        },
        "concentration": {
            "conc_gross_le_4_tdr_long": "Concentration Gross Le 4 Tdr Long",
            "conc_gross_le_4_tdr_short": "Concentration Gross Le 4 Tdr Short",
            "conc_gross_le_8_tdr_long": "Concentration Gross Le 8 Tdr Long",
            "conc_gross_le_8_tdr_short": "Concentration Gross Le 8 Tdr Short",
            "conc_net_le_4_tdr_long_all": "Concentration Net Le 4 Tdr Long All",
            "conc_net_le_4_tdr_short_all": "Concentration Net Le 4 Tdr Short All",
            "conc_net_le_8_tdr_long_all": "Concentration Net Le 8 Tdr Long All",
            "conc_net_le_8_tdr_short_all": "Concentration Net Le 8 Tdr Short All",
        },
    },
    "report_tff": {
        "positions": {
            "dealer_positions_long_all": "Dealer Positions Long All",
            "dealer_positions_short_all": "Dealer Positions Short All",
            "asset_mgr_positions_long": "Asset Manager Positions Long",
            "asset_mgr_positions_short": "Asset Manager Positions Short",
            "lev_money_positions_long": "Lev Money Positions Long",
            "lev_money_positions_short": "Lev Money Positions Short",
            "other_rept_positions_long": "Other Reportable Positions Long",
            "other_rept_positions_short": "Other Reportable Positions Short",
            "tot_rept_positions_long_all": "Total Report Positions Long All",
            "tot_rept_positions_short": "Total Report Positions Short",
            "nonrept_positions_long_all": "Non-Reportable Positions Long All",
            "nonrept_positions_short_all": "Non-Reportable Positions Short All",
        },
        "percentages": {
            "pct_of_oi_dealer_long_all": "Percentage of Open Interest (Dealer Long All)",
            "pct_of_oi_dealer_short_all": "Percentage of Open Interest (Dealer Short All)",
            "pct_of_oi_asset_mgr_long": "Percentage of Open Interest (Asset Manager Long)",
            "pct_of_oi_asset_mgr_short": "Percentage of Open Interest (Asset Manager Short)",
            "pct_of_oi_lev_money_long": "Percentage of Open Interest (Lev Money Long)",
            "pct_of_oi_lev_money_short": "Percentage of Open Interest (Lev Money Short)",
            "pct_of_oi_other_rept_long": "Percentage of Open Interest (Other Reportable Long)",
            "pct_of_oi_other_rept_short": "Percentage of Open Interest (Other Reportable Short)",
            "pct_of_oi_tot_rept_long_all": "Percentage of Open Interest (Total Report Long All)",
            "pct_of_oi_tot_rept_short": "Percentage of Open Interest (Total Report Short)",
            "pct_of_oi_nonrept_long_all": "Percentage of Open Interest (Non-Reportable Long All)",
            "pct_of_oi_nonrept_short_all": "Percentage of Open Interest (Non-Reportable Short All)",
        },
        "traders": {
            "traders_dealer_long_all": "Traders Dealer Long All",
            "traders_dealer_short_all": "Traders Dealer Short All",
            "traders_asset_mgr_long_all": "Traders Asset Manager Long All",
            "traders_asset_mgr_short_all": "Traders Asset Manager Short All",
            "traders_lev_money_long_all": "Traders Lev Money Long All",
            "traders_lev_money_short_all": "Traders Lev Money Short All",
            "traders_other_rept_long_all": "Traders Other Reportable Long All",
            "traders_other_rept_short": "Traders Other Reportable Short",
            "traders_tot_rept_long_all": "Traders Total Report Long All",
            "traders_tot_rept_short_all": "Traders Total Report Short All",
        },
        "concentration": {
            "conc_gross_le_4_tdr_long": "Concentration Gross Le 4 Tdr Long",
            "conc_gross_le_4_tdr_short": "Concentration Gross Le 4 Tdr Short",
            "conc_gross_le_8_tdr_long": "Concentration Gross Le 8 Tdr Long",
            "conc_gross_le_8_tdr_short": "Concentration Gross Le 8 Tdr Short",
            "conc_net_le_4_tdr_long_all": "Concentration Net Le 4 Tdr Long All",
            "conc_net_le_4_tdr_short_all": "Concentration Net Le 4 Tdr Short All",
            "conc_net_le_8_tdr_long_all": "Concentration Net Le 8 Tdr Long All",
            "conc_net_le_8_tdr_short_all": "Concentration Net Le 8 Tdr Short All",
        },
    },
}
