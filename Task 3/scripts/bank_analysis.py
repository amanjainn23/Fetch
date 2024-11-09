import argparse
import json
import pandas as pd


def load_and_parse_data(data):
    json_lines = [json.loads(line) for line in data.strip().split("\n")]
    return pd.DataFrame(json_lines)


def check_missing_values(df):
    missing_data = {
        "total_missing": df.isnull().sum(),
        "percent_missing": (df.isnull().sum() / len(df)) * 100,
        "total_records": len(df),
    }
    return pd.DataFrame(missing_data)


def check_duplicates(df):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df[col] = df[col].apply(str)
    duplicates = {
        "exact_duplicates": len(df) - len(df.drop_duplicates()),
        "barcode_duplicates": len(df) - len(df["barcode"].drop_duplicates()),
        "name_duplicates": len(df) - len(df["name"].drop_duplicates()),
        "brandCode_duplicates": len(df) - len(df["brandCode"].drop_duplicates()),
    }
    return duplicates


def analyze_categorical_consistency(df):
    categorical_analysis = {
        "unique_categories": df["category"].unique().tolist(),
        "unique_categoryCodes": df["categoryCode"].dropna().unique().tolist(),
        "category_counts": df["category"].value_counts().to_dict(),
        "categoryCode_counts": df["categoryCode"].value_counts().to_dict(),
    }
    return categorical_analysis


def check_barcode_validity(df):
    barcode_analysis = {
        "unique_barcode_count": len(df["barcode"].unique()),
        "barcode_length_distribution": df["barcode"].str.len().value_counts().to_dict(),
        "non_numeric_barcodes": df[~df["barcode"].str.match(r"^\d+$")][
            "barcode"
        ].tolist(),
    }
    return barcode_analysis


def analyze_brand_consistency(df):
    brand_analysis = {
        "brands_without_codes": len(df[df["brandCode"].isnull()]),
        "mismatched_names": len(df[df["name"] != df["brandCode"]]),
        "topBrand_distribution": df["topBrand"].value_counts().to_dict(),
    }
    return brand_analysis


def generate_summary_report(results, report_path):
    report = f"""
    Brand Data Quality Analysis Report
    ==========================
    
    1. Dataset Size:
    - Total Records: {results['total_records']}
    
    2. Missing Data Summary:
    - Fields with missing values: {results['missing_data'].to_dict()}
    
    3. Duplicate Analysis:
    - Exact duplicates: {results['duplicates']['exact_duplicates']}
    - Barcode duplicates: {results['duplicates']['barcode_duplicates']}
    - Name duplicates: {results['duplicates']['name_duplicates']}
    
    4. Categorical Consistency:
    - Unique categories: {len(results['categorical_analysis']['unique_categories'])}
    - Category-CategoryCode mismatches: {results['categorical_consistency_issues']}
    
    5. Barcode Analysis:
    - Unique barcodes: {results['barcode_analysis']['unique_barcode_count']}
    - Invalid format barcodes: {len(results['barcode_analysis']['non_numeric_barcodes'])}
    
    6. Brand Analysis:
    - Brands missing codes: {results['brand_analysis']['brands_without_codes']}
    - Name-Code mismatches: {results['brand_analysis']['mismatched_names']}
    """
    with open(report_path, "w") as text_file:
        text_file.write(report)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json_path",
        type=str,
        default="data/brands.json",
        help="Path for Brands JSON data",
    )
    parser.add_argument(
        "--report_path",
        type=str,
        default="report/brands.txt",
        help="Path for Brands Report",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    print(
        "\n-------------------------------------\nGenerate Report on Brands data!\n-------------------------------------\n"
    )
    args = get_args()
    print("Arguments: {}".format(vars(args)))
    print("-------------------------------------")
    with open(args.json_path, "r") as file:
        data = file.read()

    df = load_and_parse_data(data=data)
    results = {
        "total_records": len(df),
        "missing_data": check_missing_values(df),
        "duplicates": check_duplicates(df),
        "categorical_analysis": analyze_categorical_consistency(df),
        "barcode_analysis": check_barcode_validity(df),
        "brand_analysis": analyze_brand_consistency(df),
        "categorical_consistency_issues": sum(
            df["category"].notna()
            & df["categoryCode"].notna()
            & (df["category"].str.upper() != df["categoryCode"].str.replace("_", " "))
        ),
    }
    generate_summary_report(results=results, report_path=args.report_path)
    print(
        "\n-------------------------------------\nSuccessfully generated report for Brands!\n-------------------------------------\n"
    )
