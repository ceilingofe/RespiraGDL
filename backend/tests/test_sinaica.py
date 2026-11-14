from datetime import date

from app.services.sinaica import ESTACIONES_CONOCIDAS, meses, parsear_respuesta


def test_estaciones_conocidas():
    # Catálogo stations_sinaica de rsinaica (red Guadalajara/SIMAJ); 103 es Las Águilas.
    assert ESTACIONES_CONOCIDAS == {"Centro": 102, "Miravalle": 106, "Las Pintas": 104, "Santa Fe": 108}


def test_parsear_dict():
    html = '<script>var dat = [{"id":"106","fecha":"2026-01-02","hora":"7","valor":"41.5","bandO":"","val":"1"},' \
           '{"id":"106","fecha":"2026-01-02","hora":"8","valor":"","bandO":"","val":"0"}];</script>'
    f = parsear_respuesta(html)
    assert f[0] == {"fecha": "2026-01-02", "hora": 7, "valor": 41.5, "valido": 1}
    assert f[1]["valor"] is None


def test_parsear_lista_y_vacio():
    assert parsear_respuesta('var dat = [["106","2026-01-02","0","12","","1"]];')[0]["valor"] == 12.0
    assert parsear_respuesta("<html>sin datos</html>") == []


def test_meses():
    assert list(meses(date(2025, 11, 5), date(2026, 2, 1))) == [(2025, 11), (2025, 12), (2026, 1), (2026, 2)]
