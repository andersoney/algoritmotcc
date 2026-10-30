# Diretrizes e Regras de Desenvolvimento do Projeto

## 1. Regras de Commits
- **Confirmação Prévia:** NUNCA execute `git commit` sem antes apresentar as alterações detalhadas e obter a confirmação explícita do usuário.
- **Tamanho da Mensagem:** A mensagem do commit deve ser concisa, clara e objetiva, com no **máximo 300 caracteres**.
- **Formato:** Descreva o que foi alterado e o impacto no simulador ou ferramentas.

## 2. Padrões de Código e Simulação (Stage & C++)
- **Stage e Cinemática:** Ao parametrizar robôs como holonômicos no `createScenario`, definir `drive "omni"` no modelo `pioneer2dx` do arquivo `.world` gerado e controlar em translação local com `SetXSpeed()` e `SetYSpeed()`, zerando a rotação `SetTurnSpeed(0)`.
- **Sementes de Aleatoriedade (`srand`):** Sempre incorporar o ID do robô ou índice do experimento (`numExp * 1000 + numRobots`) ao chamar `srand()`, evitando que processos paralelos executados no mesmo segundo fiquem com trajetórias/posições idênticas.
- **Tempos de Simulação:** `theWorld->SimTimeNow()` retorna o tempo em microssegundos ($\mu\text{s}$) de simulação interna do Stage. Qualquer cálculo/conversão em scripts de análise deve considerar a escala de $10^6$ para segundos.

## 3. Estrutura de Documentação e Customizações
- Toda documentação técnica e guias de uso devem ser mantidos no diretório `docs/`.
- Regras e skills do assistente devem ser mantidas na pasta `.agents/`.
- Scripts auxiliares em Python que exigem dependências de terceiros devem ter alvos correspondentes no `Makefile` usando o ambiente virtual (`./venv`).

