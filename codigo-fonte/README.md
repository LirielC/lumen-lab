# LumenLab — Laboratório Computacional de Óptica

O LumenLab é uma aplicação desktop educacional para simular fenômenos de óptica física. O programa contém dois experimentos: **Interferência e Difração da Luz** e **Passagem por Polarizadores Ideais**.

Projeto desenvolvido por Liriel e Melyssa para a disciplina de Física 3, ministrada pelo professor Maurício Antolin.

A aplicação usa Python, PySide6 na interface gráfica, NumPy nos cálculos numéricos e Matplotlib nos gráficos.

A interface usa tema escuro e ícones científicos em SVG na navegação, nos cartões da tela inicial e nas ações dos experimentos. Os ícones pertencem ao projeto [Tabler Outline](https://github.com/tabler/tabler-icons) e são distribuídos localmente com sua [licença MIT](assets/icons/tabler/LICENSE). O aplicativo carrega esses recursos sem depender de conexão com a internet.

### Documentação para usuários

* [Manual de uso](documentacao/LumenLab-1.1.0-Windows/documentacao/Manual_do_Usuario_LumenLab.pdf)

## 1. Módulos

O LumenLab possui dois módulos. Em ambos, o usuário altera os parâmetros da simulação e acompanha o resultado na interface.

### 1.1 Módulo de Interferência e Difração por Fendas

O módulo simula a difração por uma fenda e o padrão de interferência com difração produzido por duas fendas.

#### Uma fenda — Difração de Fraunhofer

Para uma fenda, a intensidade luminosa é calculada por:

$$
I(\theta) = I_0 \left[ \frac{\sin\beta}{\beta} \right]^2
= I_0 \cdot \text{sinc}^2\left(\frac{a \cdot q}{\lambda}\right)
$$

onde:

$$
q = \sin\theta - \sin\alpha
$$

e

$$
\beta = \frac{\pi a}{\lambda}q
$$

A equação descreve o padrão de difração de Fraunhofer produzido pela abertura.

#### Duas fendas — Interferência com envelope de difração

Para duas fendas, o termo de interferência é multiplicado pelo envelope de difração de cada abertura:

$$
I(\theta) =
I_0 \cdot
\text{sinc}^2\left(\frac{a \cdot q}{\lambda}\right)
\cdot
\cos^2\left(\frac{\pi d \cdot q}{\lambda}\right)
$$

Nessa expressão, $d$ é a distância entre os centros das fendas e deve satisfazer $d > a$. A variável $a$ representa a largura de cada fenda.

#### Recursos disponíveis

O módulo permite:

* alternar entre uma e duas fendas;
* selecionar comprimentos de onda entre 400 e 700 nm, com uma representação aproximada da cor correspondente;
* ajustar a largura da fenda $a$, em µm;
* ajustar a separação $d$ entre as fendas, em µm;
* controlar o ângulo de incidência $\alpha$, em graus;
* ajustar a intensidade de referência $I_0$;
* visualizar o feixe incidente por meio de vetores, com sua inclinação, a linha normal de referência e o arco do ângulo $\alpha$;
* mover um marcador para definir o ângulo de observação $\theta$ e consultar seu valor numérico em tempo real;
* exibir em notação científica intensidades inferiores a milésimos;
* suavizar a representação do anteparo por superamostragem vertical;
* traçar o perfil angular $I(\theta)/I_0$ com amostragem adaptativa para representar franjas estreitas;
* alternar o gráfico entre Visão Geral e Zoom no Padrão;
* sincronizar os presets e mudar para o modo Personalizado quando um parâmetro é alterado manualmente;
* exportar os resultados em CSV;
* exportar a visualização em PNG de alta resolução.

### 1.2 Módulo de Polarização — Lei de Malus em Cascata

O módulo simula a passagem da luz por até três polarizadores ideais e calcula a intensidade transmitida em cada estágio.

#### Luz não polarizada no primeiro polarizador

Quando a luz incidente não possui direção de polarização definida, a intensidade após o primeiro polarizador é:

$$
I_1 = \frac{I_0}{2},
\qquad
\vec{E}_1 \parallel \hat{n}_{\phi_1}
$$

O primeiro polarizador transmite metade da intensidade inicial e alinha o campo elétrico ao seu eixo de transmissão.

#### Luz polarizada no primeiro polarizador

Quando a luz incidente já está polarizada em um ângulo $\phi_0$, aplica-se a Lei de Malus:

$$
I_1 = I_0 \cos^2(\phi_1 - \phi_0)
$$

#### Estágios subsequentes

Para os polarizadores seguintes, com $k \in {2, 3}$:

$$
I_k = I_{k-1}\cos^2(\phi_k - \phi_{k-1})
$$

Cada polarizador recebe a intensidade transmitida pelo estágio anterior.

#### Amplitude do campo elétrico

A razão entre a amplitude do campo elétrico em cada estágio e a amplitude inicial é:

$$
\frac{E_k}{E_0}
=
\sqrt{\frac{I_k}{I_0}}
$$

#### Recursos disponíveis

O módulo permite:

* selecionar de um a três polarizadores ideais;
* ajustar separadamente o ângulo de cada polarizador entre 0° e 180°;
* escolher entre luz incidente não polarizada e polarizada;
* definir o ângulo inicial $\phi_0$ quando a luz incidente é polarizada;
* representar o feixe não polarizado de forma isotrópica;
* visualizar os discos dos polarizadores, seus eixos de transmissão, o vetor do campo elétrico e a redução do brilho do feixe;
* consultar uma tabela com a transmissão de cada estágio e a transmissão acumulada;
* exportar os dados dos estágios em CSV.

## 2. Arquitetura da aplicação

O projeto usa Arquitetura Hexagonal, também chamada de arquitetura de Portas e Adaptadores.

As regras físicas e os casos de uso ficam separados da interface gráfica e dos mecanismos de entrada e saída. Essa divisão permite testar a lógica científica sem depender do PySide6 ou dos componentes visuais.

```text
app/
├── core/
│   ├── domain/              # Modelos imutáveis, validações e física pura em SI
│   │   ├── models/          # InterferenceParameters, PolarizationParameters, etc.
│   │   ├── physics/         # Funções matemáticas puras, sem dependências de UI
│   │   └── validation/      # Invariantes físicas: d > a, 400-700 nm, etc.
│   └── application/         # Casos de uso, DTOs e Portas (Protocols)
│       ├── dto/             # Requests e Responses
│       ├── ports/           # SimulateInterferencePort, ResultExporterPort
│       └── use_cases/       # SimulateInterferenceUseCase, SimulatePolarizationUseCase
├── adapters/
│   ├── inbound/qt/          # PySide6 Widgets, Controllers, Canvas QPainter e QSS
│   └── outbound/            # Exportação CSV e Resolvedor de Recursos (PyInstaller)
└── bootstrap/               # Container de Injeção de Dependências e inicialização
```

## 3. Instalação e execução

### Pré-requisitos

Para executar o projeto a partir do código-fonte, instale:

* Python 3.11 ou superior.

### 1. Acessar o diretório do projeto

Abra o terminal e acesse a pasta do projeto:

ex: "C:\Users\Ryzen\Downloads\LumenLabzip.zip"

### 2. Criar e ativar um ambiente virtual

O ambiente virtual mantém as dependências do projeto separadas das demais instalações do Python.

Crie o ambiente:

```
python -m venv .venv
```

No Windows PowerShell, ative-o com:

```
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

Com o ambiente virtual ativado, instale as dependências definidas em `requirements.txt`:

```
python -m pip install -r requirements.txt
```

### 4. Executar a aplicação

Inicie o LumenLab com:

```
python main.py
```

## 4. Testes automatizados

A suíte de testes cobre os cenários científicos de validação VF-01 a VF-07 e VP-01 a VP-07, além dos casos de uso e de partes da integração com a interface gráfica.

Para executar todos os testes:

```
python -m pytest -v tests/
```

Para medir a cobertura dos módulos em `app`, incluindo as diferentes ramificações do código, execute:

```
python -m coverage run -m pytest -q
python -m coverage report
python -m coverage html
```

O arquivo `.coveragerc` define uma cobertura total mínima de 50%. Se a cobertura ficar abaixo desse valor, o comando `coverage report` retorna um erro.

O relatório HTML é gerado em:

```
build/coverage/html/index.html
```

A cobertura mostra quais trechos do código os testes executaram. Ela não mede todos os cenários possíveis nem garante a ausência de bugs.

## 5. Geração do executável standalone com PyInstaller

O LumenLab pode ser empacotado como um executável independente para Windows.

Para gerar o executável portátil, execute:

```
pyinstaller packaging/LumenLab.spec
```

O arquivo é criado em:

```
dist/LumenLab.exe
```

O executável inclui o tema visual, os ícones e os demais recursos necessários ao programa. Por isso, o `LumenLab.exe` roda no Windows sem uma instalação separada do Python.


## Fontes e referências

### Física e fundamentação teórica

* **LING, Samuel J.; SANNY, Jeff; MOEBS, William.** *University Physics Volume 3*. OpenStax, 2016.
  Base teórica para difração por uma fenda, padrão de Fraunhofer, interferência e difração por duas fendas e polarização da luz.
  - [Single-Slit Diffraction](https://openstax.org/books/university-physics-volume-3/pages/4-1-single-slit-diffraction)
  - [Double-Slit Diffraction](https://openstax.org/books/university-physics-volume-3/pages/4-3-double-slit-diffraction)
  - [Polarization](https://openstax.org/books/university-physics-volume-3/pages/1-7-polarization) (Lei de Malus)
  - [Equações de difração](https://openstax.org/books/university-physics-volume-3/pages/4-key-equations)

### Arquitetura e desenvolvimento

* **COCKBURN, Alistair.** *Hexagonal Architecture — Ports and Adapters*. 2005.
  Modelo seguido na organização do projeto, mantendo as regras de domínio e os casos de uso separados da interface gráfica e dos mecanismos externos.
  [alistair.cockburn.us/hexagonal-architecture](https://alistair.cockburn.us/hexagonal-architecture/)

* **Qt.** *Qt for Python / PySide6 Documentation*.
  Framework usado na interface gráfica.
  [doc.qt.io/qtforpython-6](https://doc.qt.io/qtforpython-6/)

* **NumPy Developers.** *NumPy Documentation*.
  Biblioteca usada nos cálculos numéricos.
  [numpy.org/doc](https://numpy.org/doc/)

* **Matplotlib Development Team.** *Matplotlib Documentation*.
  Biblioteca usada para gerar os gráficos das simulações.
  [matplotlib.org/stable](https://matplotlib.org/stable/)

* **PyInstaller Development Team.** *PyInstaller Manual*.
  Ferramenta usada para empacotar a aplicação como executável standalone.
  [pyinstaller.org/en/stable](https://pyinstaller.org/en/stable/)

### Recursos gráficos

* **Tabler.** *Tabler Icons*.
  Conjunto de ícones SVG usado na interface do LumenLab, distribuído sob licença MIT.
  [tabler.io/icons](https://tabler.io/icons) · [tabler.io/license](https://tabler.io/license)
