import pytest
import pandas as pd
from utils.compute_dataframe import (
    load_csv_to_df,
    get_unique_values,
    get_filtered_values,
    get_quarter_values,
    count_unique_values,
    sum_values,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def df_basic():
    """DataFrame simple pour les tests généraux."""
    return pd.DataFrame({
        "region":   ["Île-de-France", "Bretagne", "Île-de-France", "Occitanie"],
        "valeur":   [10, 20, 30, 40],
        "code":     ["A", "B", "A", "C"],
    })

@pytest.fixture
def df_dates():
    """DataFrame avec des dates ISO8601 pour tester get_quarter_values."""
    return pd.DataFrame({
        "date":   [
            "2024-01-15T10:00:00+01:00",
            "2024-04-20T10:00:00+02:00",
            "2024-07-10T10:00:00+02:00",
            "2024-10-05T10:00:00+02:00",
        ],
        "valeur": [1, 2, 3, 4],
    })

@pytest.fixture
def csv_file(tmp_path):
    """Fichier CSV temporaire pour tester load_csv_to_df."""
    contenu = "region;valeur\nÎle-de-France;10"
    fichier = tmp_path / "test.csv"
    fichier.write_text(contenu, encoding="utf-8")
    return str(fichier)


# ── Tests load_csv_to_df ────────────────────────────────────────────────────

class TestLoadCsvToDf:
    def test_retourne_un_dataframe(self, csv_file):
        """Vérifie que la fonction retourne bien un DataFrame."""
        result = load_csv_to_df(csv_file)
        assert isinstance(result, pd.DataFrame)

    def test_colonnes_correctes(self, csv_file):
        """Vérifie que les colonnes du CSV sont bien chargées."""
        result = load_csv_to_df(csv_file)
        assert "region" in result.columns
        assert "valeur" in result.columns

    def test_nombre_lignes_correct(self, csv_file):
        """Vérifie que toutes les lignes du CSV sont chargées."""
        result = load_csv_to_df(csv_file)
        assert len(result) == 2

    def test_fichier_inexistant(self):
        """Vérifie qu'un fichier inexistant lève une erreur."""
        with pytest.raises(FileNotFoundError):
            load_csv_to_df("inexistant.csv")


# ── Tests get_unique_values ─────────────────────────────────────────────────

class TestGetUniqueValues:
    def test_retourne_valeurs_uniques(self, df_basic):
        """Vérifie que seules les valeurs distinctes sont retournées."""
        result = get_unique_values(df_basic, "region")
        assert len(result) == 3
        assert "Île-de-France" in result
        assert "Bretagne" in result
        assert "Occitanie" in result

    def test_pas_de_doublons(self, df_basic):
        """Île-de-France apparaît deux fois dans le df mais une seule fois dans unique."""
        result = get_unique_values(df_basic, "region")
        assert list(result).count("Île-de-France") == 1

    def test_colonne_inexistante(self, df_basic):
        """Vérifie qu'une colonne inexistante lève une KeyError."""
        with pytest.raises(KeyError):
            get_unique_values(df_basic, "colonne_inexistante")


# ── Tests get_filtered_values ───────────────────────────────────────────────

class TestGetFilteredValues:
    def test_filtre_une_valeur(self, df_basic):
        """Vérifie le filtrage sur une seule valeur."""
        result = get_filtered_values(df_basic, "region", ["Bretagne"])
        assert len(result) == 1
        assert result["region"].iloc[0] == "Bretagne"

    def test_filtre_plusieurs_valeurs(self, df_basic):
        """Vérifie le filtrage sur plusieurs valeurs simultanément."""
        result = get_filtered_values(df_basic, "region", ["Bretagne", "Occitanie"])
        assert len(result) == 2
        assert set(result["region"]) == {"Bretagne", "Occitanie"}

    def test_filtre_valeur_inexistante(self, df_basic):
        """Vérifie qu'un filtre sans correspondance retourne un DataFrame vide."""
        result = get_filtered_values(df_basic, "region", ["Normandie"])
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_filtre_toutes_les_valeurs(self, df_basic):
        """Vérifie que filtrer sur toutes les valeurs retourne tout le DataFrame."""
        result = get_filtered_values(df_basic, "region", ["Île-de-France", "Bretagne", "Occitanie"])
        assert len(result) == len(df_basic)


# ── Tests get_quarter_values ────────────────────────────────────────────────

class TestGetQuarterValues:
    def test_colonne_quarter_creee(self, df_dates):
        """Vérifie que la colonne quarter est bien créée."""
        result = get_quarter_values(df_dates, "date")
        assert "quarter" in result.columns

    def test_trimestres_corrects(self, df_dates):
        """Vérifie que les dates sont bien converties au bon trimestre."""
        result = get_quarter_values(df_dates, "date")
        quarters = [str(q) for q in result["quarter"]]
        assert quarters[0] == "2024Q1"  # janvier
        assert quarters[1] == "2024Q2"  # avril
        assert quarters[2] == "2024Q3"  # juillet
        assert quarters[3] == "2024Q4"  # octobre

    def test_format_date_invalide(self):
        """Vérifie qu'un format de date invalide lève une erreur."""
        df = pd.DataFrame({"date": ["pas-une-date", "2024-01-01"]})
        with pytest.raises(Exception):
            get_quarter_values(df, "date")


# ── Tests count_unique_values ───────────────────────────────────────────────

class TestCountUniqueValues:
    def test_compte_par_groupe(self, df_basic):
        """Vérifie que le comptage par groupe est correct."""
        result = count_unique_values(df_basic, "region")
        assert result["Île-de-France"] == 2
        assert result["Bretagne"] == 1
        assert result["Occitanie"] == 1

    def test_retourne_une_series(self, df_basic):
        """Vérifie que le résultat est bien une Series pandas."""
        result = count_unique_values(df_basic, "region")
        assert isinstance(result, pd.Series)

    def test_somme_egale_nombre_lignes(self, df_basic):
        """Vérifie que la somme des comptes égale le nombre total de lignes."""
        result = count_unique_values(df_basic, "region")
        assert result.sum() == len(df_basic)


# ── Tests sum_values ────────────────────────────────────────────────────────

class TestSumValues:
    def test_somme_par_groupe(self, df_basic):
        """Vérifie que la somme par groupe est correcte."""
        result = sum_values(df_basic, "valeur", "region")
        assert result["Île-de-France"] == 40  # 10 + 30
        assert result["Bretagne"] == 20
        assert result["Occitanie"] == 40

    def test_retourne_une_series(self, df_basic):
        """Vérifie que le résultat est bien une Series pandas."""
        result = sum_values(df_basic, "valeur", "region")
        assert isinstance(result, pd.Series)

    def test_colonne_inexistante(self, df_basic):
        """Vérifie qu'une colonne inexistante lève une KeyError."""
        with pytest.raises(KeyError):
            sum_values(df_basic, "colonne_inexistante", "region")