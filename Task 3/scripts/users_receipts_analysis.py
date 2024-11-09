import argparse
import json
import pandas as pd


class DataAnalyzer:
    def __init__(self):
        self.users_df = None
        self.receipts_df = None

    def load_json_data(self, json_strings):
        def parse_json_lines(data_str):
            return [
                json.loads(line)
                for line in data_str.strip().split("\n")
                if line.strip()
            ]

        if "Users" in json_strings:
            users_data = parse_json_lines(json_strings["Users"])
            self.users_df = pd.json_normalize(users_data)

        if "Receipts" in json_strings:
            receipts_data = parse_json_lines(json_strings["Receipts"])
            self.receipts_df = pd.json_normalize(receipts_data)

    def analyze_duplicates(self):
        results = {
            "users": {
                "total_records": len(self.users_df) if self.users_df is not None else 0,
                "unique_records": len(self.users_df.drop_duplicates())
                if self.users_df is not None
                else 0,
                "duplicate_ids": self.users_df["_id.$oid"].duplicated().sum()
                if self.users_df is not None
                else 0,
            },
            "receipts": {
                "total_records": len(self.receipts_df)
                if self.receipts_df is not None
                else 0,
                "unique_records": len(self.receipts_df.drop_duplicates())
                if self.receipts_df is not None
                else 0,
                "duplicate_ids": self.receipts_df["_id.$oid"].duplicated().sum()
                if self.receipts_df is not None
                else 0,
            },
        }
        return results

    def analyze_temporal_patterns(self):
        if self.users_df is not None:
            self.users_df["createdDate"] = pd.to_datetime(
                self.users_df["createdDate.$date"], unit="ms"
            )
            self.users_df["lastLogin"] = pd.to_datetime(
                self.users_df["lastLogin.$date"], unit="ms"
            )

            return {
                "date_range": {
                    "earliest_creation": self.users_df["createdDate"].min(),
                    "latest_creation": self.users_df["createdDate"].max(),
                    "earliest_login": self.users_df["lastLogin"].min(),
                    "latest_login": self.users_df["lastLogin"].max(),
                }
            }
        return None

    def analyze_user_distribution(self):
        if self.users_df is not None:
            return {
                "by_state": self.users_df["state"].value_counts().to_dict(),
                "by_role": self.users_df["role"].value_counts().to_dict(),
                "by_signup_source": self.users_df["signUpSource"]
                .value_counts()
                .to_dict(),
                "active_users": self.users_df["active"].sum(),
            }
        return None

    def check_data_consistency(self):
        consistency_issues = []

        if self.users_df is not None:
            missing_values = self.users_df.isnull().sum()
            if missing_values.any():
                consistency_issues.append(
                    f"Missing values found: {missing_values.to_dict()}"
                )
            invalid_dates = (
                self.users_df["lastLogin.$date"] < self.users_df["createdDate.$date"]
            ).sum()
            if invalid_dates > 0:
                consistency_issues.append(
                    f"Found {invalid_dates} cases where login date is before creation date"
                )
        return consistency_issues

    def generate_report(self, output_path):
        duplicate_analysis = self.analyze_duplicates()
        temporal_analysis = self.analyze_temporal_patterns()
        distribution_analysis = self.analyze_user_distribution()
        consistency_issues = self.check_data_consistency()

        report = """
        Users & Receipts Data Quality Analysis Report
        ==========================
        
        1. Duplicate Analysis
        -------------------
        Users:
        - Total Records: {users_total}
        - Unique Records: {users_unique}
        - Duplicate IDs: {users_dupes}
        
        Receipts:
        - Total Records: {receipts_total}
        - Unique Records: {receipts_unique}
        - Duplicate IDs: {receipts_dupes}
        
        2. Temporal Analysis
        ------------------
        Date Range:
        - Earliest Creation: {earliest_create}
        - Latest Creation: {latest_create}
        
        3. User Distribution
        -----------------
        By State: {state_dist}
        By Role: {role_dist}
        By Signup Source: {signup_dist}
        Active Users: {active_users}
        
        4. Data Consistency Issues
        -----------------------
        {consistency_issues}
        """.format(
            users_total=duplicate_analysis["users"]["total_records"],
            users_unique=duplicate_analysis["users"]["unique_records"],
            users_dupes=duplicate_analysis["users"]["duplicate_ids"],
            receipts_total=duplicate_analysis["receipts"]["total_records"],
            receipts_unique=duplicate_analysis["receipts"]["unique_records"],
            receipts_dupes=duplicate_analysis["receipts"]["duplicate_ids"],
            earliest_create=temporal_analysis["date_range"]["earliest_creation"]
            if temporal_analysis
            else "N/A",
            latest_create=temporal_analysis["date_range"]["latest_creation"]
            if temporal_analysis
            else "N/A",
            state_dist=distribution_analysis["by_state"]
            if distribution_analysis
            else "N/A",
            role_dist=distribution_analysis["by_role"]
            if distribution_analysis
            else "N/A",
            signup_dist=distribution_analysis["by_signup_source"]
            if distribution_analysis
            else "N/A",
            active_users=distribution_analysis["active_users"]
            if distribution_analysis
            else "N/A",
            consistency_issues="\n".join(consistency_issues)
            if consistency_issues
            else "No issues found",
        )
        with open(output_path, "w") as text_file:
            text_file.write(report)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user_json_path",
        type=str,
        default="data/users.json",
        help="Path for Users JSON data",
    )
    parser.add_argument(
        "--receipts_json_path",
        type=str,
        default="data/receipts.json",
        help="Path for Receipts JSON data",
    )
    parser.add_argument(
        "--report_path",
        type=str,
        default="report/users_receipts.txt",
        help="Path for Users and Receipts Report",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    print(
        "\n-------------------------------------\nGenerate Report on Users and Receipts data!\n-------------------------------------\n"
    )
    args = get_args()
    print("Arguments: {}".format(vars(args)))
    print("-------------------------------------")
    with open(args.user_json_path, "r") as file:
        user_data = file.read()
    with open(args.receipts_json_path, "r") as file:
        receipts_data = file.read()

    json_data = {"Users": f"{user_data}", "Receipts": f"{receipts_data}"}

    analyzer = DataAnalyzer()
    analyzer.load_json_data(json_data)
    report = analyzer.generate_report(output_path=args.report_path)
    print(
        "\n-------------------------------------\nSuccessfully generated report for Users and Receipts!\n-------------------------------------\n"
    )
