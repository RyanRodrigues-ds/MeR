"""Distância e custo de combustível das entregas, usando o OpenRouteService (openrouteservice.org).

Só usa a biblioteca padrão do Python (sem instalar nada). Precisa de internet e de uma chave gratuita.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

URL = "https://api.openrouteservice.org"


class ErroLogistica(Exception):
    """Erro com mensagem pronta para mostrar ao usuário."""


def _get(caminho, params, chave):
    url = f"{URL}{caminho}?{urllib.parse.urlencode(dict(params, api_key=chave))}"
    pedido = urllib.request.Request(url, headers={"Accept": "application/json, application/geo+json"})
    try:
        with urllib.request.urlopen(pedido, timeout=20) as resposta:
            return json.load(resposta)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise ErroLogistica("A chave do OpenRouteService foi recusada. Confira em Configurações.")
        if e.code == 429:
            raise ErroLogistica("O limite diário gratuito do OpenRouteService acabou. Tente amanhã.")
        if e.code in (400, 404) and "directions" in caminho:
            raise ErroLogistica("Não foi possível traçar uma rota até esse endereço. "
                                "Confira o endereço digitado.")
        raise ErroLogistica(f"O serviço de rotas respondeu com erro (código {e.code}).")
    except (urllib.error.URLError, TimeoutError):
        raise ErroLogistica("Sem conexão com o OpenRouteService. Verifique a internet.")
    except ValueError:
        raise ErroLogistica("Resposta inesperada do serviço de rotas.")


def geocodificar(endereco, chave, foco=None):
    """Endereço em texto -> (latitude, longitude, endereço encontrado)."""
    if not endereco.strip():
        raise ErroLogistica("Informe o endereço.")
    params = {"text": endereco.strip(), "boundary.country": "BR", "size": 1}
    if foco:  # prioriza resultados perto da base
        params["focus.point.lat"], params["focus.point.lon"] = foco
    dados = _get("/geocode/search", params, chave)
    achados = dados.get("features") or []
    if not achados:
        raise ErroLogistica("Endereço não encontrado. Escreva rua, número, bairro e cidade.")
    lon, lat = achados[0]["geometry"]["coordinates"][:2]
    return lat, lon, achados[0].get("properties", {}).get("label", endereco)


def rota(origem, destino, chave):
    """(lat, lon) -> (lat, lon): devolve (km, minutos) de um trajeto de carro."""
    dados = _get("/v2/directions/driving-car", {
        "start": f"{origem[1]},{origem[0]}", "end": f"{destino[1]},{destino[0]}"}, chave)
    try:
        resumo = dados["features"][0]["properties"]["summary"]
        return resumo["distance"] / 1000, resumo["duration"] / 60
    except (KeyError, IndexError, TypeError):
        raise ErroLogistica("O serviço de rotas não devolveu a distância.")


def custo_combustivel(km_ida, consumo_kml, preco_litro, viagens=2):
    """Retorna (km totais, litros, custo). 'viagens' = viagens de ida e volta por evento."""
    if consumo_kml <= 0:
        raise ErroLogistica("O consumo do veículo precisa ser maior que zero.")
    km_total = km_ida * 2 * viagens
    litros = km_total / consumo_kml
    return km_total, litros, litros * preco_litro


def calcular_entrega(endereco, cfg):
    """Calcula distância e custo de uma entrega. 'cfg' vem de db.todas_config()."""
    chave = cfg.get("ors_chave")
    if not chave or not cfg.get("base_lat") or not cfg.get("base_lon"):
        raise ErroLogistica("Antes, preencha em Configurações a chave do OpenRouteService "
                            "e o endereço da base.")
    base = (float(cfg["base_lat"]), float(cfg["base_lon"]))
    lat, lon, rotulo = geocodificar(endereco, chave, foco=base)
    km_ida, minutos = rota(base, (lat, lon), chave)
    viagens = int(float(cfg.get("viagens", 2)))
    km_total, litros, custo = custo_combustivel(
        km_ida, float(cfg.get("consumo_kml", 10)), float(cfg.get("preco_litro", 0)), viagens)
    return {"ok": True, "endereco": endereco, "rotulo": rotulo, "km_ida": km_ida,
            "minutos_ida": minutos, "viagens": viagens, "km_total": km_total,
            "litros": litros, "custo": custo}