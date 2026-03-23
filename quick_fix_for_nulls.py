import sqlite3


def cleanup_commodity_subgroup_nulls():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    # Update the 'commodity_subgroup_name' to 'STOCK INDICES' for specific CFTC contract market codes where the subgroup name is null, empty, or only whitespace
    cursor.execute("""
        UPDATE cftc_codes
        SET commodity_subgroup_name = 'STOCK INDICES'
        WHERE cftc_contract_market_code IN ('124603', '124608', '13874A', '13874U', '209742', '209747')
          AND (commodity_subgroup_name IS NULL OR commodity_subgroup_name = '' OR TRIM(commodity_subgroup_name) = '');
    """)
    
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Fixed {updated} rows for STOCK INDICES subgroup.")
