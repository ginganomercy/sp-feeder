import math


class PetNutritionManager:
    """
    Mengelola perhitungan porsi pakan harian berdasarkan standar FEDIAF 2024.
    """

    @staticmethod
    def calculate_daily_grams(species, category, weight_kg, kcal_per_kg):
        """
        Menghitung gram pakan harian.
        """
        # Konfigurasi Standar FEDIAF 2024
        config = {
            "cat": {"exponent": 0.67, "factors": {"junior": 250, "indoor": 75, "active": 100}},
            "dog": {"exponent": 0.75, "factors": {"junior": 200, "indoor": 95, "active": 110}},
        }

        if species.lower() not in config:
            return 0

        spec_data = config[species.lower()]
        factor = spec_data["factors"].get(category.lower(), 100)

        # Rumus: Factor * (Weight ^ Exponent)
        metabolic_weight = math.pow(weight_kg, spec_data["exponent"])
        daily_kcal_req = factor * metabolic_weight

        # Gram = (Kebutuhan Kalori / Kalori Pakan per Kg) * 1000
        daily_grams = (daily_kcal_req / kcal_per_kg) * 1000

        return round(daily_grams, 1)

    @staticmethod
    def get_hydration_requirement(weight_kg):
        """
        Estimasi kebutuhan air (ml) = 50ml - 60ml per kg berat badan.
        Digunakan untuk reminder di UI.
        """
        return round(weight_kg * 55)
