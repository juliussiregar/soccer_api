import json
from fastapi.encoders import jsonable_encoder
from typing import Tuple

class CalculateFormulas:
    ### Berat badan * Poin Aktivitas

    def two_decimals(self, input: float) -> float:
        return float("%.2f" % round(input, 2))
    def calories_max(self, berat_badan:float, poin_aktivitas:float) -> float:
        return berat_badan * poin_aktivitas

    ### Berat badan * Poin Aktivitas * 70%
    def calories_min(self, berat_badan:float, poin_aktivitas:float) -> float:
        return (self.calories_max(berat_badan, poin_aktivitas) * 70) / 100

    ### Berat badan * Poin Aktivitas * 75%
    def calories_defisit(self, berat_badan:float, poin_aktivitas:float) -> float:
        return (self.calories_max(berat_badan, poin_aktivitas) * 75) / 100

    ### 2.2 * Berat Badan
    def kebutuhan_protein(self, berat_badan: float) -> float:
        return 2.2 * berat_badan

    ### 4 * Kebutuhan Protein
    def kebutuhan_protein_calories(self, berat_badan: float):
        return self.kebutuhan_protein(berat_badan) , (4 * self.kebutuhan_protein(berat_badan))

    ### 20/100 * kalori defisit / 9
    def kebutuhan_lemak(self, berat_badan: float, poin_aktivitas: float) -> float:
        return 20 / 100 * self.calories_defisit(berat_badan, poin_aktivitas) / 9

    ### kebutuhan lemak * 9
    def kebutuhan_lemak_calories(self, berat_badan: float, poin_aktivitas: float):
        return self.kebutuhan_lemak(berat_badan, poin_aktivitas), (9 * self.kebutuhan_lemak(berat_badan, poin_aktivitas))


    ### 20/100 * kalori defisit / 9
    def kebutuhan_karbo(self, berat_badan: float, poin_aktivitas : float) -> Tuple[float, float] :
        return (self.kebutuhan_karbo_calories(berat_badan, poin_aktivitas) / 4), (self.kebutuhan_karbo_calories(berat_badan, poin_aktivitas))

    ### kebutuhan lemak * 9
    def kebutuhan_karbo_calories(self, berat_badan: float, poin_aktivitas : float) -> float:
        return (self.calories_defisit(berat_badan, poin_aktivitas) - self.kebutuhan_protein(berat_badan) - self.kebutuhan_lemak(berat_badan, poin_aktivitas))


    def basic_calculate(self, berat_badan: float, poin_aktivitas: float) :
        return self.calories_defisit(berat_badan,poin_aktivitas), self.kebutuhan_lemak(berat_badan, poin_aktivitas), self.kebutuhan_protein(berat_badan)

    def detail_calculate(self, berat_badan: float, poin_aktivitas: float):
        calories_max = self.calories_max(berat_badan, poin_aktivitas)
        calories_min = self.calories_min(berat_badan, poin_aktivitas)
        calories_defisit = self.calories_defisit(berat_badan, poin_aktivitas)
        kebutuhan_protein , kebutuhan_protein_calories = self.kebutuhan_protein_calories(berat_badan)
        kebutuhan_karbo, kebutuhan_karbo_calories = self.kebutuhan_karbo(berat_badan, poin_aktivitas)
        kebutuhan_lemak, kebutuhan_lemak_calories = self.kebutuhan_lemak_calories(berat_badan, poin_aktivitas)

        final = {
            "calories_max": self.two_decimals(calories_max),
            "calories_min": self.two_decimals(calories_min),
            "calories_defisit": self.two_decimals(calories_defisit),
            "kebutuhan_protein": self.two_decimals(kebutuhan_protein),
            "kebutuhan_protein_calories": self.two_decimals(kebutuhan_protein_calories),
            "kebutuhan_lemak": self.two_decimals(kebutuhan_lemak),
            "kebutuhan_lemak_calories": self.two_decimals(kebutuhan_lemak_calories),
            "kebutuhan_karbo": self.two_decimals(kebutuhan_karbo),
            "kebutuhan_karbo_calories": self.two_decimals(kebutuhan_karbo_calories)
        }
        encoder_final = jsonable_encoder(final)
        return json.dumps(encoder_final)




    #### TYPE DEFAULT
    ### breakfast =   20 / 100
    def breakfast(self, poin: float) -> float:
        return (20 / 100) * poin

    ### lunch = 30 / 100
    def lunch_dinner(self, poin: float) -> float:
        return (30 / 100) * poin

    ### snack = 10 / 100
    def snack(self, poin: float) -> float:
        return (10 / 100) * poin

    ### snack fat = 20 / 100
    def snack_fat(self, poin: float) -> float:
        return (20 / 100) * poin

    def calories_standard(self, poin: float, type: str):
        if type == "fat":
            return self.breakfast(poin), self.lunch_dinner(poin), self.lunch_dinner(poin), self.snack_fat(poin)
        else:
            return self.breakfast(poin), self.lunch_dinner(poin), self.lunch_dinner(poin), self.snack(poin)

    def standard_calculate(self, dct: float, dft: float, dpt: float):
        breakfast_calories, lunch_calories,\
            dinner_calories, snack_calories = self.calories_standard(dct, "calories")
        breakfast_fat, lunch_fat, \
            dinner_fat, snack_fat = self.calories_standard(dft, "fat")
        breakfast_protein, lunch_protein, \
            dinner_protein, snack_protein = self.calories_standard(dpt, "protein")

        final = {
            "breakfast_calories": self.two_decimals(breakfast_calories),
            "breakfast_fat": self.two_decimals(breakfast_fat),
            "breakfast_protein": self.two_decimals(breakfast_protein),
            "lunch_calories": self.two_decimals(lunch_calories),
            "lunch_fat": self.two_decimals(lunch_fat),
            "lunch_protein": self.two_decimals(lunch_protein),
            "dinner_calories": self.two_decimals(dinner_calories),
            "dinner_fat": self.two_decimals(dinner_fat),
            "dinner_protein": self.two_decimals(dinner_protein),
            "snack_calories": self.two_decimals(snack_calories),
            "snack_fat": self.two_decimals(snack_fat),
            "snack_protein": self.two_decimals(snack_protein),

        }
        encoder_final = jsonable_encoder(final)
        return json.dumps(encoder_final)


    def calculate_type_s(self, calc_type: int, dct:float, dft: float, dpt: float):
        if calc_type == 1:
            standard_json = self.standard_calculate(dct, dft, dpt)
            json_data = standard_json
        else:
            json_data = json.dumps('{}')

        return json_data








