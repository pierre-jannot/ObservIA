from compute_formations import compute_formation_data, compute_sirets_information, compute_departments_information

def main():
    compute_formation_data()
    compute_departments_information()
    compute_sirets_information()
    return 0

if __name__ == "__main__":
    main()