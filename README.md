# dfs
TFG -Digital file steganography 

Se necesita instalar Python 3.9

Comandos a ejecutar desde la carpeta del proyecto dfs

Instalar requerimientos para ejecutar el proyecto: 

pip install -f requirements.txt

Una vez instalado 

Para Codificar un mensaje:

python dfstego/dfstegomain.py code ruta_imagen 'mensaje_a_codificar' [lsb,pvd,emd,lsb-pvd-emd]

Decodificar un mensaje:

python dfstego/dfstegomain.py decode ruta_estego_imagen  [lsb,pvd,emd,lsb-pvd-emd]

Para ejecutar todos los test:

python -m pytest [-v] test 

Para ejecutar una clase o módulo de tests concreto:

python -m pytest [-v] ruta_clase_o_modulo_tests

Para ejecutar un test concreto:

python -m pytest [-v] ruta_clase_tests::nombre_clase_test::nombre_test_concreto

    ejemplo :

python -m pytest test/methodEMD/test_methodEMD.py::MethodEMDTest::test_transform_image_message_too_long