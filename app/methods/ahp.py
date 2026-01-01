import numpy as np

class AHP:
    """
    Utility AHP untuk menghitung bobot kriteria + Consistency Ratio (CR)
    dari matriks perbandingan berpasangan.
    """

    # Random Index (RI) Saaty untuk n=1..10 (umum dipakai)
    RI_TABLE = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
    }

    @staticmethod
    def calculate_weights(matrix: np.ndarray):
        """
        Hitung bobot dan CR dari matriks pairwise (n x n).
        Return:
          weights: list[float] panjang n (jumlah = 1)
          cr: float
        """
        if matrix is None:
            raise ValueError("Matrix is None")

        A = np.array(matrix, dtype=float)
        n = A.shape[0]

        if A.shape[0] != A.shape[1]:
            raise ValueError("Matrix harus persegi (n x n).")

        if n < 2:
            # tidak bisa AHP, tapi kembalikan bobot trivial
            return [1.0], 0.0

        # Normalisasi kolom
        col_sum = A.sum(axis=0)
        if np.any(col_sum == 0):
            raise ValueError("Ada kolom dengan jumlah 0. Pastikan semua nilai valid.")

        norm = A / col_sum

        # Priority vector (rata-rata baris)
        weights = norm.mean(axis=1)
        weights = weights / weights.sum()

        # Hitung lambda_max
        Aw = A.dot(weights)
        lambda_max = float(np.mean(Aw / weights))

        # Consistency Index (CI)
        ci = (lambda_max - n) / (n - 1)

        # Consistency Ratio (CR)
        ri = AHP.RI_TABLE.get(n, 1.49)  # fallback
        cr = 0.0 if ri == 0 else float(ci / ri)

        return weights.tolist(), cr
