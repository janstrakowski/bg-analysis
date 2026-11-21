import subprocess
import sys


def test_modul_uruchamia_pomoc():
    wynik = subprocess.run(
        [sys.executable, "-m", "narzedzia.polecenie", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert wynik.returncode == 0
    assert "paczka" in wynik.stdout
    assert "strona" in wynik.stdout
