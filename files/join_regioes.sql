SELECT
    cg.cep_inicial,
    cg.cep_final,
    COALESCE(ci.macrorregiao, uf.macrorregiao) AS macrorregiao,
    COALESCE(ci.estado, uf.estado) AS estado,
    ci.mesoregiao,
    ci.microregiao,
    ci.cidade AS cidade_inicio,
    cf.cidade as cidade_final
FROM cep_gap cg
LEFT JOIN cidades ci
    ON cg.cep_inicial  BETWEEN ci.cep_inicial AND ci.cep_final
LEFT JOIN cidades cf
    ON cg.cep_final  BETWEEN cf.cep_inicial AND cf.cep_final
LEFT JOIN estados uf
    ON cg.cep_inicial BETWEEN uf.cep_inicial AND uf.cep_final
;