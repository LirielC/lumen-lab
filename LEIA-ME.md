# LumenLab 1.1.0 — Windows

O **LumenLab** é distribuído para Windows como um executável (.exe).
Não é necessário instalar Python ou outras dependências para utilizar o programa.

## Como usar

1. Extraia todo o conteúdo do arquivo ZIP(LumenLab) para uma pasta local.
2. Abra o arquivo `LumenLab.exe`.
3. Na primeira execução, aguarde alguns segundos — o Windows costuma levar um tempo verificando o executável antes de abrir.
4. Para orientações sobre os experimentos e funcionalidades, consulte o [Manual do Usuário](LumenLab/documentacao/Manual_do_Usuario_LumenLab.pdf).

> Não execute o programa direto de dentro do ZIP. Extraia todos os arquivos antes de abrir o `LumenLab.exe`, ou o programa pode não funcionar corretamente.

## Em caso de erro

### O programa não abre

Verifique primeiro se:

- todo o conteúdo do ZIP foi extraído;
- o `LumenLab.exe` está sendo executado a partir de uma pasta local;
- os arquivos que acompanham o executável não foram removidos ou movidos;
- o antivírus ou o Windows Security não bloqueou algum arquivo durante a extração.

Se necessário, extraia novamente o ZIP para uma nova pasta e tente executar o programa outra vez.

### O Windows exibe um aviso de segurança

Dependendo das configurações do sistema, o Windows pode exibir um aviso ao abrir um executável baixado da internet.

Antes de prosseguir, confira se o arquivo veio da fonte correta e, se quiser, valide sua integridade com os hashes em `SHA256SUMS.txt`.

### O aplicativo abre, mas apresenta erro ou comportamento inesperado

Consulte a pasta `evidencias/`, que contém registros da verificação local da versão distribuída, incluindo resultados de testes e capturas de tela.

Se o problema continuar, registre:

- a mensagem de erro exibida;
- a versão do Windows utilizada;
- o momento em que o problema ocorreu;
- uma captura de tela, quando possível.

## Conteúdo do pacote

- `LumenLab.exe` — aplicativo para Windows de 64 bits.
- `documentacao/` — manual de uso do LumenLab.
- `codigo-fonte/` — código-fonte, recursos, testes, dependências e configuração de compilação.
- `evidencias/` — resultados da verificação local, testes e capturas em resolução 1366x768.
- `SHA256SUMS.txt` — hashes SHA-256 para conferência da integridade dos arquivos.

## Requisitos

- Windows de 64 bits.
- Não é necessário instalar Python.
- Não é necessário acesso à internet para utilizar o aplicativo.