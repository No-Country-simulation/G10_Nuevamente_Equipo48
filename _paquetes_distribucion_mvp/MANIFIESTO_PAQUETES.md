# Manifiesto de paquetes

Este manifiesto se genera tras terminar los paquetes. Incluye SHA-256 de cada archivo distribuido y excluye ZIPs para evitar dependencia circular.

| Paquete | Archivo | SHA-256 |
| --- | --- | --- |
| Alexis | `alexis/INSTRUCCIONES.md` | `9ba6c2651afe025f0c4b41d1dca318c87b20c071305d064632a1e386863cb8c5` |
| Alexis | `alexis/patches/nuevo-corpus-loader.patch` | `6cc0d43cc4fa505ce58c59c1088d73bc54ff4dc3edb1609a3baba704a9bf6424` |
| Alexis | `alexis/patches/precarga-corpus-y-rag.patch` | `bd06e119e92dd2b3e3593b5ae6653a9fcf5364856c56584caf3ba40ca9ae4343` |
| Coordinación | `coordinacion/INSTRUCCIONES.md` | `37b603634ca380a26b37901d796528c9bddeb11b4b473911f76614ac3c1f6f33` |
| Dayanara | `dayanara/INSTRUCCIONES.md` | `0ec4901685d67408351a648eff7427d37dfe53fac2066a9af96fd3fb291a60dd` |
| Dayanara | `dayanara/patches/nuevo-test-cliente-frontend.patch` | `ac206b10f318bc0ce528826f31ca41dc283dacb416d5b37659e004cb6b393ce4` |
| Dayanara | `dayanara/patches/nuevo-test-corpus-loader.patch` | `c1506606e0e7bde1ba75ef7bdd93e6d1ed07f33cf5a28195f910ea14798d95ef` |
| Dayanara | `dayanara/patches/tests-existentes.patch` | `5b352ccf05dd1d80d078c9e155c7ae8bd2f91f953f4d2fcc8ff9d7098b3d0d42` |
| Raíz | `INFORME_COMPARACION.md` | `a904ba83617b343b89c5342fcdb5abfc2157fb63fc30405743a3c43a51454080` |
| Jaime | `jaime/INSTRUCCIONES.md` | `b4393fc89c5c4c6c5b3d43a3356ec737507840ea772152c60e2e2a8ca57b8032` |
| Jaime | `jaime/patches/agentes-orquestacion.patch` | `b27f9bf6ab49b5bbb955056fe1d821cb6724d9d68b55873a5ef7a2e0d7032108` |
| Mariana | `mariana/INSTRUCCIONES.md` | `289ada7152bd04e37129bbeb9aa0aca3209855441428e6778bde7b02fe993658` |
| Mariana | `mariana/patches/backend-api-contract.patch` | `5e74179969ecc3fbc9e1050982b403df157bcde5e5696cc8cca88cc1b6534c5a` |
| Mónica | `monica/INSTRUCCIONES.md` | `00c4a020d07b1f4a215be91ee63fa7f73fa981b88fe59790907d863052084604` |
| Mónica | `monica/patches/frontend-streamlit-api.patch` | `4e738f3abb818266235e489f0b6f9286f7b31869786418d81a92008c83e80d3f` |
| Raíz | `PLAN_INTEGRACION.md` | `4c202b55f83f4eb838508367b9527b42730baac4983ded2d93dc7bc6bc7798cc` |
| ZIP Alexis | `alexis.zip` | `411b274792c0271ccbb52481f9c9c94d1185241e3bcebbd0ad99655436e9455a` |
| ZIP Coordinación | `coordinacion.zip` | `4ec5215c75edecabb643187534bdb9acf762179fb98e54acf9e693a8b07c330e` |
| ZIP Dayanara | `dayanara.zip` | `b68838c47eeaf4c708f744912d7170647a405d5ab701616d041998a06c68ed51` |
| ZIP Jaime | `jaime.zip` | `5c1cb1c619bd566db71b4dfa6326777b6392fa2adb5d917c25c85621c6c26768` |
| ZIP Mariana | `mariana.zip` | `00e1fb7ca2d10aca42e098ca2cf760d49aa4f099d1cb536fc18f77f4b32a97d7` |
| ZIP Mónica | `monica.zip` | `88e9e7c4d0128458b322f12b083b68fa6cf487c0cd54c7df055d4ec48d2574e3` |

## Exclusiones deliberadas

- Secretos y archivos `.env`.
- Entornos virtuales, cachés, bytecode y ejecutables.
- PDFs, hojas de cálculo y demás binarios del corpus/evidencia.
- Material no rastreado que no sea necesario para aplicar un cambio de código separado.
