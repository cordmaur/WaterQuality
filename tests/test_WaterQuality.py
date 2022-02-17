from waterquality.WaterQuality import main
from sys import argv
from pathlib import Path


def test_script():
    try:
        # Simulate a call to the script passing no arguments
        argv.clear()
        argv.append('D:/OneDrive - Agência Nacional de Águas/Projects/WaterQuality/waterquality/WaterQuality.py')
        main()

        # test the GetConfig option
        argv.append('-GC')
        main()

        # Check if both WaterQuality and WaterDetect .ini exists
        path = Path(__file__).parent
        assert (path/'WaterQuality.ini').exists()
        (path/'WaterQuality.ini').unlink()

        assert (path/'WaterDetect.ini').exists()
        (path/'WaterDetect.ini').unlink()

        assert True

    except Exception as e:
        print(e)
        assert False


def test_run_single():
    assert True
