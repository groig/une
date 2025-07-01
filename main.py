import json
import re
from typing import List, Dict, Optional


class CubanEnergyReportExtractor:
    def __init__(self):
        # Pattern to identify daily energy reports
        self.report_patterns = [
            # Original pattern with emoji
            r"📢\s*Nota Informativa - Situación del SEN al (\d{1,2} de \w+ de \d{4})",
            # New pattern without emoji, with period and "para el"
            r"Nota informativa\.\s*\n?\s*Situación del SEN para el (\d{1,2} de \w+ de \d{4})",
            # More flexible pattern to catch variations
            r"Nota [iI]nformativa[.\-\s]*\n?\s*Situación del SEN (?:al|para el) (\d{1,2} de \w+ de \d{4})",
            # Even more flexible pattern
            r"(?:📢\s*)?Nota [iI]nformativa[.\-\s]*(?:\n?\s*)?Situación del SEN (?:al|para el) (\d{1,2} de \w+ de \d{4})",
            # Pattern for messages that start directly with "Situación del SEN"
            r"^Situación del SEN para el (\d{1,2} de \w+ de \d{4})",
        ]

    def load_telegram_data(self, file_path: str) -> Dict:
        """Load the exported Telegram JSON data"""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_daily_report(self, message_text: str) -> bool:
        """Check if a message is a daily energy report"""
        try:
            for pattern in self.report_patterns:
                if re.search(pattern, message_text, re.IGNORECASE | re.MULTILINE):
                    return True
        except:
            import pudb

            pudb.set_trace()

    def extract_date_from_report(self, message_text: str) -> Optional[str]:
        """Extract the report date from the message text"""
        for pattern in self.report_patterns:
            match = re.search(pattern, message_text)
            if match:
                return match.group(1)
        return None

    def clean_report_text(self, text: str) -> str:
        """Clean the report text by removing emojis and formatting"""
        # Remove emojis (basic cleanup)
        emoji_pattern = r"[\U0001F300-\U0001F9FF]|[\U0001F600-\U0001F64F]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]"
        text = re.sub(emoji_pattern, "", text)

        # Remove extra whitespace and normalize
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def extract_energy_data(self, text: str) -> Dict:
        """Extract specific energy metrics from the report text"""
        data = {}

        # Helper function to clean numbers (remove commas and convert to int)
        def clean_number(match_obj):
            if match_obj:
                return int(match_obj.group(1).replace(",", ""))
            return None

        # Extract current availability - multiple patterns
        availability_patterns = [
            r"Disponibilidad:\s*([\d,]+)\s*MW",  # Original format
            r"disponibilidad del SEN a las \d{2}:\d{2} horas es de ([\d,]+) MW",  # New format
            r"disponibilidad de ([\d,]+) MW",  # Generic format
        ]

        for pattern in availability_patterns:
            availability_match = re.search(pattern, text, re.IGNORECASE)
            if availability_match:
                data["availability_mw"] = clean_number(availability_match)
                break

        # Extract current demand - multiple patterns
        demand_patterns = [
            r"Demanda:\s*([\d,]+)\s*MW",  # Original format
            r"la demanda ([\d,]+) MW",  # New format
            r"demanda de ([\d,]+) MW",  # Alternative format
        ]

        for pattern in demand_patterns:
            demand_match = re.search(pattern, text, re.IGNORECASE)
            if demand_match:
                data["demand_mw"] = clean_number(demand_match)
                break

        # Extract current deficit/affectation - multiple patterns
        affectation_patterns = [
            r"Afectación actual:\s*([\d,]+)\s*MW",  # Original format
            r"con ([\d,]+) MW afectados",  # New format
            r"afectación de ([\d,]+) MW",  # Generic format
        ]

        for pattern in affectation_patterns:
            affectation_match = re.search(pattern, text, re.IGNORECASE)
            if affectation_match:
                data["current_affectation_mw"] = clean_number(affectation_match)
                break

        # Extract peak hour projections - improved patterns
        peak_availability_patterns = [
            r"Se proyecta una disponibilidad de ([\d,]+) MW",  # Original
            r"se estima una disponibilidad de ([\d,]+) MW",  # New format
            r"disponibilidad de ([\d,]+) MW.*(?:horario pico|pico)",  # Generic peak availability
        ]

        for pattern in peak_availability_patterns:
            peak_availability_match = re.search(pattern, text, re.IGNORECASE)
            if peak_availability_match:
                data["peak_projected_availability_mw"] = clean_number(
                    peak_availability_match
                )
                break

        # Peak demand - improved patterns
        peak_demand_patterns = [
            r"una demanda de ([\d,]+)",  # Original
            r"demanda máxima de ([\d,]+) MW",  # New format
            r"y una demanda de ([\d,]+)",  # Alternative
        ]

        for pattern in peak_demand_patterns:
            peak_demand_match = re.search(pattern, text, re.IGNORECASE)
            if peak_demand_match:
                data["peak_projected_demand_mw"] = clean_number(peak_demand_match)
                break

        # Peak deficit - improved patterns
        peak_deficit_patterns = [
            r"déficit de ([\d,]+) MW",  # Original
            r"para un déficit de ([\d,]+) MW",  # New format
            r"un déficit de ([\d,]+) MW",  # Alternative
        ]

        for pattern in peak_deficit_patterns:
            peak_deficit_match = re.search(pattern, text, re.IGNORECASE)
            if peak_deficit_match:
                data["peak_projected_deficit_mw"] = clean_number(peak_deficit_match)
                break

        # Peak affectation - improved patterns
        peak_affectation_patterns = [
            r"para una afectación de ([\d,]+) MW",  # Original
            r"afectación estimada de ([\d,]+) MW",  # Alternative original
            r"se pronostica una afectación de ([\d,]+) MW",  # New format
            r"afectación de ([\d,]+) MW en este horario",  # New format specific
        ]

        for pattern in peak_affectation_patterns:
            peak_affectation_match = re.search(pattern, text, re.IGNORECASE)
            if peak_affectation_match:
                data["peak_projected_affectation_mw"] = clean_number(
                    peak_affectation_match
                )
                break

        # Extract midday affectation estimate (new field for June 18th format)
        midday_affectation_patterns = [
            r"en el horario de la media se estima una afectación de ([\d,]+) MW",
            r"horario de la media.*afectación de ([\d,]+) MW",
            r"Pronóstico para el mediodía:\s*([\d,]+) MW afectados",
        ]

        for pattern in midday_affectation_patterns:
            midday_match = re.search(pattern, text, re.IGNORECASE)
            if midday_match:
                data["midday_projected_affectation_mw"] = clean_number(midday_match)
                break

        # Extract solar production - improved patterns
        solar_production_patterns = [
            r"Producción de energía de los \d+ parques solares fotovoltaicos: ([\d,]+) MWh",  # Original
            r"La producción de energía de los \d+ nuevos parques solares fotovoltaicos fue de ([\d,]+) MWh",  # New format
            r"producción.*parques solares.*fue de ([\d,]+) MWh",  # Generic
        ]

        for pattern in solar_production_patterns:
            solar_production_match = re.search(pattern, text, re.IGNORECASE)
            if solar_production_match:
                data["solar_production_mwh"] = clean_number(solar_production_match)
                # Convert MWh to average MW (assuming 6 hours of production)
                data["solar_production_mw"] = clean_number(solar_production_match) / 6
                break

        # Extract solar peak power
        solar_peak_patterns = [
            r"con ([\d,]+) MW como máxima potencia",  # Both formats use this
        ]

        for pattern in solar_peak_patterns:
            solar_peak_match = re.search(pattern, text, re.IGNORECASE)
            if solar_peak_match:
                data["solar_peak_power_mw"] = clean_number(solar_peak_match)
                break

        # Extract previous day's maximum affectation
        prev_affectation_patterns = [
            r"máxima afectación (?:en el día de ayer )?fue de ([\d,]+) MW",  # Original
            r"La máxima afectación en el día de ayer fue de ([\d,]+) MW",  # Both formats
        ]

        for pattern in prev_affectation_patterns:
            prev_affectation_match = re.search(pattern, text, re.IGNORECASE)
            if prev_affectation_match:
                data["previous_day_max_affectation_mw"] = clean_number(
                    prev_affectation_match
                )
                break

        return data

    def process_messages(self, telegram_data: Dict) -> List[Dict]:
        """Process all messages and extract daily reports"""
        reports = []

        for message in telegram_data.get("messages", []):
            # Skip non-message types
            if message.get("type") != "message":
                continue

            message_text = message.get("text", "")

            if isinstance(message_text, dict):
                continue

            if isinstance(message_text, list):
                message_text = message_text[0]

            if isinstance(message_text, dict):
                continue

            # Check if this is a daily report
            if self.is_daily_report(message_text):
                # Extract message date
                message_date = message.get("date", "")

                # Extract report date from text
                report_date = self.extract_date_from_report(message_text)

                # Clean the text
                # cleaned_text = self.clean_report_text(message_text)

                # Extract structured data
                energy_data = self.extract_energy_data(message_text)

                report = {
                    "message_date": message_date,
                    "report_date": report_date,
                    # "original_text": message_text,
                    # "cleaned_text": cleaned_text,
                    "energy_data": energy_data,
                    "message_id": message.get("id"),
                }

                reports.append(report)

        return reports

    def save_cleaned_reports(self, reports: List[Dict], output_file: str):
        """Save the cleaned reports to a JSON file"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

    def print_summary(self, reports: List[Dict]):
        """Print a summary of extracted reports"""
        print("\n=== EXTRACTION SUMMARY ===")
        print(f"Total daily reports found: {len(reports)}")

        for i, report in enumerate(reports, 1):
            print(f"\nReport {i}:")
            print(f"  Date: {report['report_date']}")
            print(f"  Message Date: {report['message_date']}")

            energy_data = report["energy_data"]
            if energy_data:
                print(
                    f"  Current Availability: {energy_data.get('availability_mw', 'N/A')} MW"
                )
                print(f"  Current Demand: {energy_data.get('demand_mw', 'N/A')} MW")
                print(
                    f"  Current Deficit: {energy_data.get('current_affectation_mw', 'N/A')} MW"
                )
                print(
                    f"  Avg Solar Production (6 hrs): {energy_data.get('solar_production_mw', 'N/A')} MW"
                )
                print(
                    f"  Midday Projected Affectation: {energy_data.get('midday_projected_affectation_mw', 'N/A')} MW"
                )


# Example usage
def main():
    extractor = CubanEnergyReportExtractor()

    # Load the data (assuming the JSON file is named 'result.json')
    try:
        telegram_data = extractor.load_telegram_data("raw/result.json")

        # Process messages and extract reports
        reports = extractor.process_messages(telegram_data)

        # Save cleaned reports
        extractor.save_cleaned_reports(reports, "data.json")

        # Print summary
        # extractor.print_summary(reports)

        print("\nCleaned reports saved to 'data.json'")

    except FileNotFoundError:
        print(
            "Error: result.json file not found. Please make sure the file exists in the current directory."
        )
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the input file.")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        print("Full traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
