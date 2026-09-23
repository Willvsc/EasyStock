const formulario = document.getElementById("produtoForm");
const tabela = document.getElementById("tabelaProdutos");
const pesquisa = document.getElementById("pesquisa");
const contador = document.getElementById("contador");
const semProdutos = document.getElementById("semProdutos");
const mensagem = document.getElementById("mensagem");

const filtroProduto =
    document.getElementById("filtroProduto");

const filtroTipo =
    document.getElementById("filtroTipo");

const filtroData =
    document.getElementById("filtroData");

const btnLimparFiltros =
    document.getElementById("btnLimparFiltros");

const btnNovaCategoria =
    document.getElementById("btnNovaCategoria");

if (btnNovaCategoria) {

    btnNovaCategoria.addEventListener(
        "click",
        abrirNovaCategoria
    );

}

let produtos = [];


// ==============================
// CARREGAR PRODUTOS
// ==============================

async function carregarProdutos() {

    try {

        const resposta =
            await fetch("/api/produtos");

       produtos =
    await resposta.json();
carregarFiltroCategoriasProdutos();

// Atualiza os cards somente quando
// os elementos do Dashboard antigo existirem.

if (
    document.getElementById("semEstoque") &&
    document.getElementById("valorEstoque")
) {

    atualizarDashboard();

}


renderizarProdutos();

    } catch (erro) {

        console.error(
            "Erro ao carregar produtos:",
            erro
        );

        mostrarMensagem(
            "Não foi possível carregar os produtos.",
            "erro"
        );

    }
    

}


function carregarFiltroCategoriasProdutos() {

    const filtroCategoria =
        document.getElementById(
            "filtroCategoriaProdutos"
        );

    if (!filtroCategoria) {
        return;
    }

    const categoriaSelecionada =
        filtroCategoria.value;

    const categorias = [
        ...new Set(
            produtos.map(
                produto => produto.categoria
            )
        )
    ].sort();


    filtroCategoria.innerHTML = `
        <option value="">
            Todas as categorias
        </option>
    `;


    categorias.forEach(categoria => {

        const opcao =
            document.createElement("option");

        opcao.value = categoria;
        opcao.textContent = categoria;

        filtroCategoria.appendChild(opcao);

    });


    filtroCategoria.value =
        categoriaSelecionada;

}
// ==============================
// RENDERIZAR TABELA DE PRODUTOS
// ==============================

function renderizarProdutos() {

    const termo =
        pesquisa.value
            .toLowerCase()
            .trim();

    semProdutos.style.display = "none";

    const filtroCategoria =
    document.getElementById(
        "filtroCategoriaProdutos"
    );

const categoriaSelecionada =
    filtroCategoria
        ? filtroCategoria.value
        : "";

    const produtosFiltrados =
        produtos.filter(produto => {

           const correspondePesquisa =
    produto.nome
        .toLowerCase()
        .includes(termo) ||

    produto.sku
        .toLowerCase()
        .includes(termo);


const correspondeCategoria =
    categoriaSelecionada === "" ||
    produto.categoria === categoriaSelecionada;


return (
    correspondePesquisa &&
    correspondeCategoria
);

        });


    tabela.innerHTML = "";


    contador.textContent =
        `${produtos.length} produto${produtos.length !== 1 ? "s" : ""} cadastrado${produtos.length !== 1 ? "s" : ""}`;


    if (produtosFiltrados.length === 0) {

        semProdutos.style.display = "block";

        return;

    }


    semProdutos.style.display = "none";


    produtosFiltrados.forEach(produto => {

        const linha =
            document.createElement("tr");


        // ==============================
        // STATUS DO ESTOQUE
        // ==============================

        let statusTexto;
        let statusClasse;
        let linhaClasse;


        if (produto.quantidade === 0) {

            statusTexto = "Sem estoque";
            statusClasse = "status-critico";
            linhaClasse = "linha-critica";

        } else if (produto.quantidade < 5) {

            statusTexto = "Estoque baixo";
            statusClasse = "status-alerta";
            linhaClasse = "linha-alerta";

        } else {

            statusTexto = "Estoque normal";
            statusClasse = "status-ok";
            linhaClasse = "";

        }


        linha.className =
            linhaClasse;


        linha.innerHTML = `

            <td>
                <strong>
                    ${escaparHTML(produto.nome)}
                </strong>
            </td>

           <td>
    ${escaparHTML(produto.categoria)}
</td>

<td>
    R$ ${Number(produto.preco)
        .toFixed(2)
        .replace(".", ",")}
</td>

<td>

    <div class="controle-quantidade">

        <button
            class="btn-quantidade btn-menos"
            onclick="alterarQuantidade(${produto.id}, 'remover')"
            title="Remover unidade"
        >
            −
        </button>

        <span class="quantidade">
            ${produto.quantidade}
        </span>

        <button
            class="btn-quantidade btn-mais"
            onclick="alterarQuantidade(${produto.id}, 'adicionar')"
            title="Adicionar unidade"
        >
            +
        </button>

    </div>

</td>

<td>
    ${escaparHTML(produto.sku)}
</td>

<td>
    <span class="status ${statusClasse}">
        ${statusTexto}
    </span>
</td>

<td>

    <button
        type="button"
        class="btn-editar"
        onclick="abrirEdicao(${produto.id})"
        title="Editar produto"
    >
        ✏️
    </button>

    <button
        type="button"
        class="btn-excluir"
        onclick="excluirProduto(${produto.id})"
        title="Excluir produto"
    >
        🗑️
    </button>

</td>

`;


        tabela.appendChild(linha);

    });

}


// ==============================
// CADASTRAR PRODUTO
// ==============================

if (formulario) {

    formulario.addEventListener(
        "submit",
        async (evento) => {

        evento.preventDefault();


        const dados = {

            nome:
                document.getElementById("nome").value,

            categoria:
                document.getElementById("categoria").value,

            preco:
                document.getElementById("preco").value,

            quantidade:
                document.getElementById("quantidade").value,

            sku:
                document.getElementById("sku").value

        };


        try {

            const resposta =
                await fetch(
                    "/api/produtos",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(dados)
                    }
                );


            const resultado =
                await resposta.json();


            if (!resposta.ok) {

                throw new Error(
                    resultado.erro
                );

            }


            mostrarMensagem(
                resultado.mensagem,
                "sucesso"
            );


            formulario.reset();
            
            fecharModalNovoProduto();


            await carregarProdutos();


        } catch (erro) {

            mostrarMensagem(
                erro.message,
                "erro"
            );

        }

    }
);
}


// ==============================
// ALTERAR QUANTIDADE
// ==============================

async function alterarQuantidade(
    id,
    operacao
) {

    try {

        const resposta =
            await fetch(
                `/api/produtos/${id}/quantidade`,
                {

                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            operacao: operacao
                        })

                }
            );


        const resultado =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                resultado.erro
            );

        }


        await carregarProdutos();

        await carregarMovimentacoes();


    } catch (erro) {

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}


// ==============================
// EXCLUIR PRODUTO
// ==============================

let produtoIdParaExcluir = null;


function excluirProduto(id) {

    const produto =
        produtos.find(
            produto => produto.id === id
        );

    if (!produto) {
        return;
    }


    produtoIdParaExcluir = id;


    const nomeProduto =
        document.getElementById(
            "nomeProdutoExcluir"
        );

    if (nomeProduto) {
        nomeProduto.textContent =
            produto.nome;
    }


    const modal =
        document.getElementById(
            "modalExcluirProduto"
        );

    if (modal) {
        modal.classList.add("ativo");
    }

}
// ==============================
// MODAL - EXCLUIR PRODUTO
// ==============================

const modalExcluirProduto =
    document.getElementById("modalExcluirProduto");

const btnFecharExcluirProduto =
    document.getElementById("btnFecharExcluirProduto");

const btnCancelarExcluirProduto =
    document.getElementById("btnCancelarExcluirProduto");


function fecharModalExcluirProduto() {

    if (!modalExcluirProduto) {
        return;
    }

    modalExcluirProduto.classList.remove("ativo");

    produtoIdParaExcluir = null;

}


if (btnFecharExcluirProduto) {

    btnFecharExcluirProduto.addEventListener(
        "click",
        fecharModalExcluirProduto
    );

}


if (btnCancelarExcluirProduto) {

    btnCancelarExcluirProduto.addEventListener(
        "click",
        fecharModalExcluirProduto
    );

}


// Fechar ao clicar fora do modal
if (modalExcluirProduto) {

    modalExcluirProduto.addEventListener(
        "click",
        (evento) => {

            if (evento.target === modalExcluirProduto) {
                fecharModalExcluirProduto();
            }

        }
    );

}

// ==============================
// PESQUISA DE PRODUTOS
// ==============================

if (pesquisa) {

    pesquisa.addEventListener(
        "input",
        renderizarProdutos
    );

}

const filtroCategoriaProdutos =
    document.getElementById(
        "filtroCategoriaProdutos"
    );

if (filtroCategoriaProdutos) {

    filtroCategoriaProdutos.addEventListener(
        "change",
        renderizarProdutos
    );

}


// ==============================
// MENSAGENS
// ==============================

function mostrarMensagem(
    texto,
    tipo
) {

    mensagem.textContent =
        texto;

    mensagem.className =
        `mensagem ${tipo}`;


    setTimeout(() => {

        mensagem.className =
            "mensagem";

    }, 3000);

}


// ==============================
// SEGURANÇA
// ==============================

function escaparHTML(texto) {

    const elemento =
        document.createElement("div");

    elemento.textContent =
        texto;

    return elemento.innerHTML;

}

async function carregarCategoriasEdicao() {

    const selectCategoria =
        document.getElementById(
            "editarCategoria"
        );

    if (!selectCategoria) {
        return;
    }

    try {

        const resposta =
            await fetch("/api/categorias");

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar as categorias."
            );
        }

        const categorias =
            await resposta.json();

            categorias.sort(
    (a, b) =>
        a.nome.localeCompare(
            b.nome,
            "pt-BR",
            {
                sensitivity: "base"
            }
        )
);

        selectCategoria.innerHTML = `
            <option value="">
                Selecione uma categoria
            </option>
        `;


        categorias.forEach(categoria => {

            const opcao =
                document.createElement("option");

            opcao.value =
                categoria.nome;

            opcao.textContent =
                categoria.nome;

            selectCategoria.appendChild(
                opcao
            );

        });

    } catch (erro) {

        console.error(
            "Erro ao carregar categorias da edição:",
            erro
        );

    }

}

// ==============================
// ABRIR EDIÇÃO
// ==============================

async function abrirEdicao(id) {

    const produto =
        produtos.find(
            produto => produto.id === id
        );


    if (!produto) {
        return;
    }
await carregarCategoriasEdicao();

    document.getElementById(
        "editarId"
    ).value =
        produto.id;


    document.getElementById(
        "editarNome"
    ).value =
        produto.nome;


    const selectCategoria =
        document.getElementById(
            "editarCategoria"
        );


    const categoriaExiste =
        Array.from(
            selectCategoria.options
        ).some(
            option =>
                option.value ===
                produto.categoria
        );


    if (
        !categoriaExiste &&
        produto.categoria
    ) {

        const novaOpcao =
            document.createElement(
                "option"
            );

        novaOpcao.value =
            produto.categoria;

        novaOpcao.textContent =
            `${produto.categoria} (atual)`;

        selectCategoria.appendChild(
            novaOpcao
        );

    }


    selectCategoria.value =
        produto.categoria;


    document.getElementById(
        "editarPreco"
    ).value =
        produto.preco;


    document.getElementById(
        "editarSku"
    ).value =
        produto.sku;


    document.getElementById(
        "modalEdicao"
    ).classList.add("ativo");

}


// ==============================
// FECHAR EDIÇÃO
// ==============================

function fecharEdicao() {

    document.getElementById(
        "modalEdicao"
    ).classList.remove("ativo");

}


// ==============================
// SALVAR EDIÇÃO
// ==============================

async function salvarEdicao(evento) {

    evento.preventDefault();


    const id =
        document.getElementById(
            "editarId"
        ).value;


    const dados = {

        nome:
            document.getElementById(
                "editarNome"
            ).value,

        categoria:
            document.getElementById(
                "editarCategoria"
            ).value,

        preco:
            document.getElementById(
                "editarPreco"
            ).value,

        sku:
            document.getElementById(
                "editarSku"
            ).value

    };


    try {

        const resposta =
            await fetch(
                `/api/produtos/${id}`,
                {

                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(dados)

                }
            );


        const resultado =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                resultado.erro
            );

        }


        fecharEdicao();


        mostrarMensagem(
            resultado.mensagem,
            "sucesso"
        );


        await carregarProdutos();


    } catch (erro) {

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}


// ==============================
// CATEGORIAS
// ==============================

async function carregarCategorias() {

    try {

        const resposta =
            await fetch(
                "/api/categorias"
            );


        const categorias =
            await resposta.json();


        const lista =
            document.getElementById(
                "listaCategorias"
            );


        const selectCategoria =
            document.getElementById(
                "categoria"
            );


        const selectEditarCategoria =
            document.getElementById(
                "editarCategoria"
            );


        // ==============================
        // LISTA DE CATEGORIAS
        // ==============================

       if (lista) {
    lista.innerHTML = "";
}

      categorias.forEach(
    categoria => {

        const item =
            document.createElement(
                "div"
            );


        item.className =
            "categoria-item";


        const quantidadeProdutos =
            categoria.quantidade_produtos || 0;


        const textoQuantidade =
            quantidadeProdutos === 1
                ? "1 produto"
                : `${quantidadeProdutos} produtos`;


        item.innerHTML = `

            <div class="categoria-nome">

                <div class="categoria-icone">
                    ▣
                </div>

                <span>
                    ${escaparHTML(
                        categoria.nome
                    )}
                </span>

            </div>


            <div class="categoria-quantidade">

                ${textoQuantidade}

            </div>


            <div class="categoria-acoes">

                <button
                    type="button"
                    class="btn-editar"
                    onclick="abrirEdicaoCategoria(${categoria.id})"
                    title="Editar categoria"
                >
                    ✏️
                </button>

                <button
                    type="button"
                    class="btn-excluir"
                    onclick="excluirCategoria(${categoria.id})"
                    title="Excluir categoria"
                >
                    🗑️
                </button>

            </div>

        `;


        if (lista) {
            lista.appendChild(item);
        }

    }
);


        // ==============================
        // SELECT DO CADASTRO
        // ==============================

        if (selectCategoria) {

    selectCategoria.innerHTML = `
        <option value="">
            Selecione uma categoria
        </option>
    `;

}

        // ==============================
        // SELECT DA EDIÇÃO
        // ==============================

       if (selectEditarCategoria) {

    selectEditarCategoria.innerHTML = `
        <option value="">
            Selecione uma categoria
        </option>
    `;

}

        categorias.forEach(
            categoria => {

                const opcaoCadastro =
                    document.createElement(
                        "option"
                    );


                opcaoCadastro.value =
                    categoria.nome;


                opcaoCadastro.textContent =
                    categoria.nome;


             if (selectCategoria) {

    selectCategoria.appendChild(
        opcaoCadastro
    );

}


if (selectEditarCategoria) {

    const opcaoEdicao =
        document.createElement(
            "option"
        );

    opcaoEdicao.value =
        categoria.nome;

    opcaoEdicao.textContent =
        categoria.nome;

    selectEditarCategoria.appendChild(
        opcaoEdicao
    );

}  
            }
        );


  } catch (erro) {

    console.error(
        "ERRO EM carregarCategorias:",
        erro
    );

    mostrarMensagem(
        "Não foi possível carregar as categorias.",
        "erro"
    );

}

}


if (document.getElementById("listaCategorias")) {

    carregarCategorias();

}


// ==============================
// NOVA CATEGORIA
// ==============================

function abrirNovaCategoria() {

    document
        .getElementById(
            "modalCategoria"
        )
        .classList.add("ativo");


    document
        .getElementById(
            "novaCategoria"
        )
        .focus();

}


function fecharNovaCategoria() {

    document
        .getElementById(
            "modalCategoria"
        )
        .classList.remove("ativo");


    document
        .getElementById(
            "formCategoria"
        )
        .reset();

}


async function salvarNovaCategoria(
    evento
) {

    evento.preventDefault();


    const nome =
        document
            .getElementById(
                "novaCategoria"
            )
            .value
            .trim();


    if (!nome) {
        return;
    }


    try {

        const resposta =
            await fetch(
                "/api/categorias",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            nome: nome
                        })

                }
            );


        const resultado =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                resultado.erro
            );

        }


        fecharNovaCategoria();


        mostrarMensagem(
            resultado.mensagem,
            "sucesso"
        );


        await carregarCategorias();


    } catch (erro) {

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}


// ==============================
// EDITAR CATEGORIA
// ==============================
async function abrirEdicaoCategoria(id) {

    try {

        const resposta =
            await fetch("/api/categorias");

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar a categoria."
            );
        }


        const categorias =
            await resposta.json();


        const categoria =
            categorias.find(
                categoria =>
                    categoria.id === id
            );


        if (!categoria) {
            return;
        }


        document.getElementById(
            "editarCategoriaId"
        ).value =
            categoria.id;


        document.getElementById(
            "editarNomeCategoria"
        ).value =
            categoria.nome;


        document.getElementById(
            "modalEditarCategoria"
        ).classList.add("ativo");


        document.getElementById(
            "editarNomeCategoria"
        ).focus();


    } catch (erro) {

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}

// ==============================
// EXCLUIR CATEGORIA
// ==============================

let categoriaIdParaExcluir = null;


async function excluirCategoria(id) {

    try {

        const resposta =
            await fetch("/api/categorias");


        if (!resposta.ok) {

            throw new Error(
                "Não foi possível carregar a categoria."
            );

        }


        const categorias =
            await resposta.json();


        const categoria =
            categorias.find(
                categoria =>
                    categoria.id === id
            );


        if (!categoria) {
            return;
        }


        categoriaIdParaExcluir = id;


        const nomeCategoria =
            document.getElementById(
                "nomeCategoriaExcluir"
            );


        if (nomeCategoria) {

            nomeCategoria.textContent =
                categoria.nome;

        }


        const modal =
            document.getElementById(
                "modalExcluirCategoria"
            );


        if (modal) {
            modal.classList.add("ativo");
        }


    } catch (erro) {

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}

// ==============================
// DASHBOARD
// ==============================

function atualizarDashboard() {

    const totalProdutos =
        document.getElementById(
            "totalProdutos"
        );


    const totalItens =
        document.getElementById(
            "totalItens"
        );


    const estoqueBaixo =
        document.getElementById(
            "estoqueBaixo"
        );


    const semEstoque =
        document.getElementById(
            "semEstoque"
        );


    const valorEstoque =
        document.getElementById(
            "valorEstoque"
        );


    let quantidadeTotal = 0;

    let quantidadeEstoqueBaixo = 0;

    let quantidadeSemEstoque = 0;

    let valorTotalEstoque = 0;


    produtos.forEach(
        produto => {

            const quantidade =
                Number(
                    produto.quantidade
                );


            const preco =
                Number(
                    produto.preco
                );


            quantidadeTotal +=
                quantidade;


            valorTotalEstoque +=
                preco * quantidade;


            if (quantidade === 0) {

                quantidadeSemEstoque++;

            } else if (
                quantidade < 5
            ) {

                quantidadeEstoqueBaixo++;

            }

        }
    );


    totalProdutos.textContent =
        produtos.length;


    totalItens.textContent =
        quantidadeTotal;


    estoqueBaixo.textContent =
        quantidadeEstoqueBaixo;


    semEstoque.textContent =
        quantidadeSemEstoque;


    valorEstoque.textContent =
        valorTotalEstoque.toLocaleString(
            "pt-BR",
            {
                style: "currency",
                currency: "BRL"
            }
        );

}


// ==============================
// HISTÓRICO DE MOVIMENTAÇÕES
// ==============================

// =========================================================
// NOVOS FILTROS DO HISTÓRICO
// =========================================================

const filtroProdutoSelect =
    document.getElementById(
        "filtroProdutoSelect"
    );

const filtroCategoriaHistorico =
    document.getElementById(
        "filtroCategoriaHistorico"
    );


// =========================================================
// CARREGAR MOVIMENTAÇÕES
// =========================================================

async function carregarMovimentacoes() {

    try {

        const resposta =
            await fetch(
                "/api/movimentacoes"
            );


        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar as movimentações."
            );
        }


        const movimentacoes =
            await resposta.json();


        // =================================================
        // CONTADORES DE ENTRADAS E SAÍDAS
        // =================================================

        const totalEntradas =
            document.getElementById(
                "totalEntradas"
            );


        const totalSaidas =
            document.getElementById(
                "totalSaidas"
            );


        let quantidadeEntradas = 0;
        let quantidadeSaidas = 0;


        movimentacoes.forEach(
            movimentacao => {

                if (
                    movimentacao.tipo ===
                    "entrada"
                ) {

                    quantidadeEntradas +=
                        Number(
                            movimentacao.quantidade
                        );

                }


                if (
                    movimentacao.tipo ===
                    "saida"
                ) {

                    quantidadeSaidas +=
                        Number(
                            movimentacao.quantidade
                        );

                }

            }
        );


        if (totalEntradas) {

            totalEntradas.textContent =
                quantidadeEntradas;

        }


        if (totalSaidas) {

            totalSaidas.textContent =
                quantidadeSaidas;

        }


        // =================================================
        // ELEMENTOS DA TABELA
        // =================================================

        const tabela =
            document.getElementById(
                "tabelaMovimentacoes"
            );


        const semMovimentacoes =
            document.getElementById(
                "semMovimentacoes"
            );


        if (!tabela || !semMovimentacoes) {
            return;
        }


        // =================================================
        // PREENCHER SELECT DE PRODUTOS
        // =================================================

        if (filtroProdutoSelect) {

            const valorAtualProduto =
                filtroProdutoSelect.value;


            const produtosUnicos =
                new Map();


            movimentacoes.forEach(
                movimentacao => {

                    if (
                        movimentacao.produto_id &&
                        movimentacao.produto_nome
                    ) {

                        produtosUnicos.set(
                            String(
                                movimentacao.produto_id
                            ),
                            movimentacao.produto_nome
                        );

                    }

                }
            );


            const produtosOrdenados =
                Array.from(
                    produtosUnicos.entries()
                ).sort(
                    (a, b) =>
                        a[1].localeCompare(
                            b[1],
                            "pt-BR"
                        )
                );


            filtroProdutoSelect.innerHTML = `
                <option value="todos">
                    Todos os produtos
                </option>
            `;


            produtosOrdenados.forEach(
                ([id, nome]) => {

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value = id;

                    option.textContent =
                        nome;

                    filtroProdutoSelect.appendChild(
                        option
                    );

                }
            );


            const produtoAindaExiste =
                Array.from(
                    filtroProdutoSelect.options
                ).some(
                    option =>
                        option.value ===
                        valorAtualProduto
                );


            filtroProdutoSelect.value =
                produtoAindaExiste
                    ? valorAtualProduto
                    : "todos";

        }


        // =================================================
        // PREENCHER SELECT DE CATEGORIAS
        // =================================================

        if (filtroCategoriaHistorico) {

            const valorAtualCategoria =
                filtroCategoriaHistorico.value;


            const categoriasUnicas =
                new Map();


            movimentacoes.forEach(
                movimentacao => {

                    if (
                        movimentacao.categoria_id &&
                        movimentacao.categoria
                    ) {

                        categoriasUnicas.set(
                            String(
                                movimentacao.categoria_id
                            ),
                            movimentacao.categoria
                        );

                    }

                }
            );


            const categoriasOrdenadas =
                Array.from(
                    categoriasUnicas.entries()
                ).sort(
                    (a, b) =>
                        a[1].localeCompare(
                            b[1],
                            "pt-BR"
                        )
                );


            filtroCategoriaHistorico.innerHTML = `
                <option value="todas">
                    Todas as categorias
                </option>
            `;


            categoriasOrdenadas.forEach(
                ([id, nome]) => {

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value = id;

                    option.textContent =
                        nome;

                    filtroCategoriaHistorico.appendChild(
                        option
                    );

                }
            );


            const categoriaAindaExiste =
                Array.from(
                    filtroCategoriaHistorico.options
                ).some(
                    option =>
                        option.value ===
                        valorAtualCategoria
                );


            filtroCategoriaHistorico.value =
                categoriaAindaExiste
                    ? valorAtualCategoria
                    : "todas";

        }


        // =================================================
        // VALORES DOS FILTROS
        // =================================================

        const termoProduto =
            filtroProduto
                ? filtroProduto.value
                    .toLowerCase()
                    .trim()
                : "";


        const produtoSelecionado =
            filtroProdutoSelect
                ? filtroProdutoSelect.value
                : "todos";


        const categoriaSelecionada =
            filtroCategoriaHistorico
                ? filtroCategoriaHistorico.value
                : "todas";


        const tipoSelecionado =
            filtroTipo
                ? filtroTipo.value
                : "todos";


        const dataSelecionada =
            filtroData
                ? filtroData.value
                : "";


        // =================================================
        // APLICAR FILTROS
        // =================================================

        const movimentacoesFiltradas =
            movimentacoes.filter(
                movimentacao => {

                    // PESQUISA PELO NOME

                    const nomeProduto =
                        movimentacao.produto_nome
                            ? movimentacao.produto_nome
                                .toLowerCase()
                            : "";


                    const correspondePesquisa =
                        nomeProduto.includes(
                            termoProduto
                        );


                    // PRODUTO ESPECÍFICO

                    const correspondeProduto =
                        produtoSelecionado ===
                            "todos" ||
                        String(
                            movimentacao.produto_id
                        ) ===
                            produtoSelecionado;


                    // CATEGORIA

                    const correspondeCategoria =
                        categoriaSelecionada ===
                            "todas" ||
                        String(
                            movimentacao.categoria_id
                        ) ===
                            categoriaSelecionada;


                    // TIPO

                    const correspondeTipo =
                        tipoSelecionado ===
                            "todos" ||
                        movimentacao.tipo ===
                            tipoSelecionado;


                    // DATA

                    let correspondeData =
                        true;


                    if (dataSelecionada) {

                        correspondeData =
                            movimentacao.data_hora &&
                            movimentacao.data_hora
                                .startsWith(
                                    dataSelecionada
                                );

                    }


                    return (
                        correspondePesquisa &&
                        correspondeProduto &&
                        correspondeCategoria &&
                        correspondeTipo &&
                        correspondeData
                    );

                }
            );


        // =================================================
        // LIMPAR TABELA
        // =================================================

        tabela.innerHTML = "";


        // =================================================
        // NENHUMA MOVIMENTAÇÃO
        // =================================================

        if (
            movimentacoesFiltradas.length ===
            0
        ) {

            semMovimentacoes.style.display =
                "block";

            return;

        }


        semMovimentacoes.style.display =
            "none";


        // =================================================
        // RENDERIZAR MOVIMENTAÇÕES
        // =================================================

        movimentacoesFiltradas.forEach(
            movimentacao => {

                const linha =
                    document.createElement(
                        "tr"
                    );


                const entrada =
                    movimentacao.tipo ===
                    "entrada";


                const tipoTexto =
                    entrada
                        ? "📥 Entrada"
                        : "📤 Saída";


                const tipoClasse =
                    entrada
                        ? "movimentacao-entrada"
                        : "movimentacao-saida";


                const data =
                    new Date(
                        movimentacao.data_hora
                            .replace(
                                " ",
                                "T"
                            )
                    );


                const dataFormatada =
                    data.toLocaleString(
                        "pt-BR",
                        {
                            day: "2-digit",
                            month: "2-digit",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit"
                        }
                    );


                const categoria =
                    movimentacao.categoria
                        ? escaparHTML(
                            movimentacao.categoria
                        )
                        : "—";


                const usuario =
                    movimentacao.usuario_nome
                        ? escaparHTML(
                            movimentacao.usuario_nome
                        )
                        : "—";


                linha.innerHTML = `

                    <td>
                        ${escaparHTML(
                            movimentacao.produto_nome ||
                            "Produto removido"
                        )}
                    </td>


                    <td>
                        ${categoria}
                    </td>


                    <td>

                        <span class="${tipoClasse}">
                            ${tipoTexto}
                        </span>

                    </td>


                    <td>

                        <span
                            class="movimentacao-quantidade ${
                                entrada
                                    ? "entrada"
                                    : "saida"
                            }"
                        >
                            ${
                                entrada
                                    ? "+"
                                    : "-"
                            }${movimentacao.quantidade}
                        </span>

                    </td>


                    <td>
                        ${dataFormatada}
                    </td>


                    <td>
                        ${usuario}
                    </td>

                `;


                tabela.appendChild(
                    linha
                );

            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar movimentações:",
            erro
        );

    }

}


// =========================================================
// EVENTOS DOS FILTROS DO HISTÓRICO
// =========================================================


// PESQUISA

if (filtroProduto) {

    filtroProduto.addEventListener(
        "input",
        carregarMovimentacoes
    );

}


// PRODUTO

if (filtroProdutoSelect) {

    filtroProdutoSelect.addEventListener(
        "change",
        carregarMovimentacoes
    );

}


// CATEGORIA

if (filtroCategoriaHistorico) {

    filtroCategoriaHistorico.addEventListener(
        "change",
        carregarMovimentacoes
    );

}


// TIPO

if (filtroTipo) {

    filtroTipo.addEventListener(
        "change",
        carregarMovimentacoes
    );

}


// DATA

if (filtroData) {

    filtroData.addEventListener(
        "change",
        carregarMovimentacoes
    );

}


// =========================================================
// LIMPAR TODOS OS FILTROS
// =========================================================

if (btnLimparFiltros) {

    btnLimparFiltros.addEventListener(
        "click",
        () => {

            if (filtroProduto) {
                filtroProduto.value = "";
            }


            if (filtroProdutoSelect) {
                filtroProdutoSelect.value =
                    "todos";
            }


            if (filtroCategoriaHistorico) {
                filtroCategoriaHistorico.value =
                    "todas";
            }


            if (filtroTipo) {
                filtroTipo.value =
                    "todos";
            }


            if (filtroData) {
                filtroData.value =
                    "";
            }


            carregarMovimentacoes();

        }
    );

}

// ==============================
// INICIALIZAÇÃO
// ==============================

window.addEventListener(
    "load",
    () => {

        // ==============================
        // PÁGINA DE PRODUTOS
        // ==============================

        if (
            document.getElementById("produtoForm") ||
            document.getElementById("tabelaProdutos")
        ) {

            carregarProdutos();

        }


        // ==============================
        // PÁGINA DE HISTÓRICO
        // ==============================

        if (
            document.getElementById("tabelaMovimentacoes") &&
            document.getElementById("filtroProduto")
        ) {

            carregarMovimentacoes();

        }


        // ==============================
        // SESSÃO
        // ==============================

        verificarSessao();

    }
);
async function carregarPerfisUsuarios() {

    const selectPerfil =
        document.getElementById("usuarioPerfil");

    if (!selectPerfil) {
        return;
    }

    try {

        const resposta =
            await fetch("/api/perfis");

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar os perfis."
            );
        }

        const perfis =
            await resposta.json();


        selectPerfil.innerHTML = `
            <option value="">
                Selecione um perfil
            </option>
        `;


        perfis.forEach(
            function (perfil) {

                const option =
                    document.createElement("option");

                option.value =
                    perfil.id;

                option.textContent =
                    perfil.nome;

                selectPerfil.appendChild(option);

            }
        );

    } catch (erro) {

        console.error(
            "Erro ao carregar perfis:",
            erro
        );

        selectPerfil.innerHTML = `
            <option value="">
                Erro ao carregar perfis
            </option>
        `;

    }

}
const formUsuario =
    document.getElementById("formUsuario");

if (formUsuario) {

    formUsuario.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const mensagemUsuario =
                document.getElementById("mensagemUsuario");

            mensagemUsuario.textContent = "";


            const nome =
                document.getElementById("usuarioNome").value.trim();

            const email =
                document.getElementById("usuarioEmail").value.trim();

            const senha =
                document.getElementById("usuarioSenha").value;

            const perfilId =
                document.getElementById("usuarioPerfil").value;


            try {

                const resposta = await fetch(
                    "/api/usuarios",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            nome: nome,
                            email: email,
                            senha: senha,
                            perfil_id: Number(perfilId)
                        })
                    }
                );


                const dados =
                    await resposta.json();


                if (!resposta.ok) {

                    mensagemUsuario.textContent =
                        dados.erro ||
                        "Não foi possível cadastrar o usuário.";

                    return;
                }


                mensagemUsuario.textContent =
                    "Usuário cadastrado com sucesso.";

                formUsuario.reset();

                carregarUsuarios();
            } catch (erro) {

                console.error(
                    "Erro ao cadastrar usuário:",
                    erro
                );

                mensagemUsuario.textContent =
                    "Erro ao conectar com o servidor.";

            }

        }
    );

}
async function carregarUsuarios() {

    const tabelaUsuarios =
        document.getElementById("tabelaUsuarios");

    if (!tabelaUsuarios) {
        return;
    }

    try {

        const resposta =
            await fetch("/api/usuarios");

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar os usuários."
            );
        }

        const usuarios =
            await resposta.json();


        tabelaUsuarios.innerHTML = "";


        usuarios.forEach(
            function (usuario) {

                const linha =
                    document.createElement("tr");


                const colunaNome =
                    document.createElement("td");

                colunaNome.textContent =
                    usuario.nome;


                const colunaEmail =
                    document.createElement("td");

                colunaEmail.textContent =
                    usuario.email;


                const colunaPerfil =
                    document.createElement("td");

                colunaPerfil.textContent =
                    usuario.perfil;


                linha.appendChild(colunaNome);
                linha.appendChild(colunaEmail);
                linha.appendChild(colunaPerfil);

                tabelaUsuarios.appendChild(linha);

            }
        );

    } catch (erro) {

        console.error(
            "Erro ao carregar usuários:",
            erro
        );

    }

}
async function verificarSessao() {

    const secaoUsuarios =
        document.getElementById("secaoUsuarios");

    try {

        const resposta =
            await fetch("/api/sessao");


        if (!resposta.ok) {

            window.location.href = "/login";

            return;
        }


        const dados =
            await resposta.json();


        if (
            secaoUsuarios &&
            dados.usuario.perfil === "Administrador"
        ) {

            secaoUsuarios.style.display = "";

            carregarPerfisUsuarios();
            carregarUsuarios();

        }

    } catch (erro) {

        console.error(
            "Erro ao verificar sessão:",
            erro
        );

    }

}
// ==============================
// NOVO DASHBOARD
// ==============================

async function carregarNovoDashboard() {

    // Executa somente se estivermos
    // na nova página de Dashboard.
    const totalProdutosElemento =
        document.getElementById("totalProdutos");

    if (!totalProdutosElemento) {
        return;
    }

    try {

        // ==============================
        // PRODUTOS
        // ==============================

        const respostaProdutos =
            await fetch("/api/produtos");

        if (!respostaProdutos.ok) {
            throw new Error(
                "Não foi possível carregar os produtos."
            );
        }

        const produtos =
            await respostaProdutos.json();


        const totalProdutos =
            produtos.length;

        const totalItens =
            produtos.reduce(
                (total, produto) =>
                    total + Number(produto.quantidade || 0),
                0
            );

        const produtosEstoqueBaixo =
            produtos.filter(
                produto =>
                    Number(produto.quantidade) > 0 &&
                    Number(produto.quantidade) <= 5
            );


        document.getElementById(
            "totalProdutos"
        ).textContent = totalProdutos;


        document.getElementById(
            "totalItens"
        ).textContent = totalItens;


        document.getElementById(
            "estoqueBaixo"
        ).textContent =
            produtosEstoqueBaixo.length;


        // ==============================
        // MOVIMENTAÇÕES
        // ==============================

        const respostaMovimentacoes =
            await fetch("/api/movimentacoes");

        if (!respostaMovimentacoes.ok) {
            throw new Error(
                "Não foi possível carregar as movimentações."
            );
        }

        const movimentacoes =
            await respostaMovimentacoes.json();


        const entradas =
            movimentacoes.filter(
                movimentacao =>
                    movimentacao.tipo === "entrada"
            );

        const saidas =
            movimentacoes.filter(
                movimentacao =>
                    movimentacao.tipo === "saida"
            );


        document.getElementById(
            "totalMovimentacoes"
        ).textContent =
            movimentacoes.length;

        // ==============================
        // LISTA DE ESTOQUE BAIXO
        // ==============================

        const lista =
            document.getElementById(
                "listaEstoqueBaixo"
            );

        if (!lista) {
            return;
        }


        if (produtosEstoqueBaixo.length === 0) {

            lista.innerHTML = `
                <p class="dashboard-vazio">
                    Nenhum produto com estoque baixo.
                </p>
            `;

            return;
        }


        lista.innerHTML =
            produtosEstoqueBaixo
                .slice(0, 5)
                .map(produto => `
                    <div class="dashboard-produto-baixo">

                        <div>
                            <strong>
                                ${produto.nome}
                            </strong>

                            <span>
                                ${produto.sku}
                                ·
                                ${produto.categoria}
                            </span>
                        </div>

                        <span class="dashboard-quantidade-baixa">
                            ${produto.quantidade} un.
                        </span>

                    </div>
                `)
                .join("");

    } catch (erro) {

        console.error(
            "Erro ao carregar Dashboard:",
            erro
        );

    }

}

// ==============================
// MODAL - NOVO PRODUTO
// ==============================

const btnNovoProduto =
    document.getElementById("btnNovoProduto");

const modalNovoProduto =
    document.getElementById("modalNovoProduto");

const btnFecharNovoProduto =
    document.getElementById("btnFecharNovoProduto");

const btnCancelarNovoProduto =
    document.getElementById("btnCancelarNovoProduto");


function abrirModalNovoProduto() {

    if (!modalNovoProduto) {
        return;
    }

    carregarCategoriasNovoProduto();

    modalNovoProduto.classList.add("ativo");

}


function fecharModalNovoProduto() {

    if (!modalNovoProduto) {
        return;
    }

    modalNovoProduto.classList.remove("ativo");


    const formularioProduto =
        document.getElementById("produtoForm");

    if (formularioProduto) {
        formularioProduto.reset();
    }

}


if (btnNovoProduto) {

    btnNovoProduto.addEventListener(
        "click",
        abrirModalNovoProduto
    );

}


if (btnFecharNovoProduto) {

    btnFecharNovoProduto.addEventListener(
        "click",
        fecharModalNovoProduto
    );

}


if (btnCancelarNovoProduto) {

    btnCancelarNovoProduto.addEventListener(
        "click",
        fecharModalNovoProduto
    );

}
if (modalNovoProduto) {

    modalNovoProduto.addEventListener(
        "click",
        (evento) => {

            if (evento.target === modalNovoProduto) {
                fecharModalNovoProduto();
            }

        }
    );

}
async function carregarCategoriasNovoProduto() {

    const selectCategoria =
        document.getElementById("categoria");

    if (!selectCategoria) {
        return;
    }

    try {

        const resposta =
            await fetch("/api/categorias");

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar as categorias."
            );
        }

        const categorias =
            await resposta.json();


        selectCategoria.innerHTML = `
            <option value="">
                Selecione uma categoria
            </option>
        `;


        categorias.forEach(categoria => {

            const opcao =
                document.createElement("option");

            /*
             * O cadastro de produto atual trabalha
             * com o nome da categoria no formulário.
             */
            opcao.value = categoria.nome;
            opcao.textContent = categoria.nome;

            selectCategoria.appendChild(opcao);

        });

    } catch (erro) {

        console.error(
            "Erro ao carregar categorias:",
            erro
        );

    }

}
// ==============================
// MODAL - EDITAR PRODUTO
// FECHAR AO CLICAR FORA
// ==============================

const modalEdicao =
    document.getElementById("modalEdicao");

if (modalEdicao) {

    modalEdicao.addEventListener(
        "click",
        (evento) => {

            if (evento.target === modalEdicao) {
                fecharEdicao();
            }

        }
    );

}
const btnConfirmarExcluirProduto =
    document.getElementById(
        "btnConfirmarExcluirProduto"
    );


if (btnConfirmarExcluirProduto) {

    btnConfirmarExcluirProduto.addEventListener(
        "click",
        async () => {

            if (!produtoIdParaExcluir) {
                return;
            }

            try {

                const resposta =
                    await fetch(
                        `/api/produtos/${produtoIdParaExcluir}`,
                        {
                            method: "DELETE"
                        }
                    );


                const resultado =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        resultado.erro
                    );

                }


                fecharModalExcluirProduto();


                mostrarMensagem(
                    resultado.mensagem,
                    "sucesso"
                );


                await carregarProdutos();

            } catch (erro) {

                mostrarMensagem(
                    erro.message,
                    "erro"
                );

            }

        }
    );

}

document.addEventListener(
    "DOMContentLoaded",
    carregarNovoDashboard
);
// ==============================
// MODAL - NOVA CATEGORIA
// ==============================

const modalCategoria =
    document.getElementById("modalCategoria");

const btnFecharCategoria =
    document.getElementById("btnFecharCategoria");

const btnCancelarCategoria =
    document.getElementById("btnCancelarCategoria");


// BOTÃO X
if (btnFecharCategoria) {

    btnFecharCategoria.addEventListener(
        "click",
        fecharNovaCategoria
    );

}


// BOTÃO CANCELAR
if (btnCancelarCategoria) {

    btnCancelarCategoria.addEventListener(
        "click",
        fecharNovaCategoria
    );

}


// CLIQUE FORA DO MODAL
if (modalCategoria) {

    modalCategoria.addEventListener(
        "click",
        (evento) => {

            if (evento.target === modalCategoria) {
                fecharNovaCategoria();
            }

        }
    );

}
const modalEditarCategoria =
    document.getElementById(
        "modalEditarCategoria"
    );

const btnFecharEditarCategoria =
    document.getElementById(
        "btnFecharEditarCategoria"
    );

const btnCancelarEditarCategoria =
    document.getElementById(
        "btnCancelarEditarCategoria"
    );


function fecharModalEditarCategoria() {

    if (!modalEditarCategoria) {
        return;
    }

    modalEditarCategoria.classList.remove(
        "ativo"
    );

}


if (btnFecharEditarCategoria) {

    btnFecharEditarCategoria.addEventListener(
        "click",
        fecharModalEditarCategoria
    );

}


if (btnCancelarEditarCategoria) {

    btnCancelarEditarCategoria.addEventListener(
        "click",
        fecharModalEditarCategoria
    );

}


if (modalEditarCategoria) {

    modalEditarCategoria.addEventListener(
        "click",
        (evento) => {

            if (
                evento.target ===
                modalEditarCategoria
            ) {

                fecharModalEditarCategoria();

            }

        }
    );

}
const formEditarCategoria =
    document.getElementById(
        "formEditarCategoria"
    );


if (formEditarCategoria) {

    formEditarCategoria.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();


            const id =
                document.getElementById(
                    "editarCategoriaId"
                ).value;


            const nome =
                document.getElementById(
                    "editarNomeCategoria"
                ).value.trim();


            if (!nome) {

                mostrarMensagem(
                    "Digite um nome para a categoria.",
                    "erro"
                );

                return;

            }


            try {

                const resposta =
                    await fetch(
                        `/api/categorias/${id}`,
                        {
                            method: "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    nome: nome
                                })
                        }
                    );


                const resultado =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        resultado.erro
                    );

                }


                fecharModalEditarCategoria();


                mostrarMensagem(
                    resultado.mensagem,
                    "sucesso"
                );


                await carregarCategorias();


            } catch (erro) {

                mostrarMensagem(
                    erro.message,
                    "erro"
                );

            }

        }
    );

}
const modalExcluirCategoria =
    document.getElementById(
        "modalExcluirCategoria"
    );

const btnFecharExcluirCategoria =
    document.getElementById(
        "btnFecharExcluirCategoria"
    );

const btnCancelarExcluirCategoria =
    document.getElementById(
        "btnCancelarExcluirCategoria"
    );


function fecharModalExcluirCategoria() {

    if (!modalExcluirCategoria) {
        return;
    }


    modalExcluirCategoria.classList.remove(
        "ativo"
    );


    categoriaIdParaExcluir = null;

}


// BOTÃO X
if (btnFecharExcluirCategoria) {

    btnFecharExcluirCategoria.addEventListener(
        "click",
        fecharModalExcluirCategoria
    );

}


// BOTÃO CANCELAR
if (btnCancelarExcluirCategoria) {

    btnCancelarExcluirCategoria.addEventListener(
        "click",
        fecharModalExcluirCategoria
    );

}


// CLIQUE FORA
if (modalExcluirCategoria) {

    modalExcluirCategoria.addEventListener(
        "click",
        (evento) => {

            if (
                evento.target ===
                modalExcluirCategoria
            ) {

                fecharModalExcluirCategoria();

            }

        }
    );

}
const btnConfirmarExcluirCategoria =
    document.getElementById(
        "btnConfirmarExcluirCategoria"
    );


if (btnConfirmarExcluirCategoria) {

    btnConfirmarExcluirCategoria.addEventListener(
        "click",
        async () => {

            if (!categoriaIdParaExcluir) {
                return;
            }


            try {

                const resposta =
                    await fetch(
                        `/api/categorias/${categoriaIdParaExcluir}`,
                        {
                            method: "DELETE"
                        }
                    );


                const resultado =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        resultado.erro
                    );

                }


                fecharModalExcluirCategoria();


                mostrarMensagem(
                    resultado.mensagem,
                    "sucesso"
                );


                await carregarCategorias();


            } catch (erro) {

                mostrarMensagem(
                    erro.message,
                    "erro"
                );

            }

        }
    );

}
async function carregarProdutosMovimentacao() {

    const selectProduto =
        document.getElementById(
            "movimentacaoProduto"
        );


    if (!selectProduto) {
        return;
    }


    try {

        const resposta =
            await fetch("/api/produtos");


        if (!resposta.ok) {

            throw new Error(
                "Não foi possível carregar os produtos."
            );

        }


        const produtos =
            await resposta.json();


        selectProduto.innerHTML = `
            <option value="">
                Selecione um produto
            </option>
        `;


        produtos.forEach(
            produto => {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    produto.id;


                option.textContent =
                    `${produto.nome} · ${produto.quantidade} disponíveis`;


                option.dataset.quantidade =
                    produto.quantidade;


                selectProduto.appendChild(
                    option
                );

            }
        );


    } catch (erro) {

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}
if (
    document.getElementById(
        "movimentacaoProduto"
    )
) {

    carregarProdutosMovimentacao();

}
const btnRegistrarEntrada =
    document.getElementById(
        "btnRegistrarEntrada"
    );

const btnRegistrarSaida =
    document.getElementById(
        "btnRegistrarSaida"
    );

const movimentacaoTipo =
    document.getElementById(
        "movimentacaoTipo"
    );

const movimentacaoProduto =
    document.getElementById(
        "movimentacaoProduto"
    );


if (
    btnRegistrarEntrada &&
    movimentacaoTipo
) {

    btnRegistrarEntrada.addEventListener(
        "click",
        () => {

            movimentacaoTipo.value =
                "adicionar";

            if (movimentacaoProduto) {
                movimentacaoProduto.focus();
            }

        }
    );

}


if (
    btnRegistrarSaida &&
    movimentacaoTipo
) {

    btnRegistrarSaida.addEventListener(
        "click",
        () => {

            movimentacaoTipo.value =
                "remover";

            if (movimentacaoProduto) {
                movimentacaoProduto.focus();
            }

        }
    );

}
const formMovimentacao =
    document.getElementById(
        "formMovimentacao"
    );

const erroMovimentacao =
    document.getElementById(
        "erroMovimentacao"
    );


if (formMovimentacao) {

    formMovimentacao.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();


            const selectProduto =
                document.getElementById(
                    "movimentacaoProduto"
                );

            const selectTipo =
                document.getElementById(
                    "movimentacaoTipo"
                );

            const inputQuantidade =
                document.getElementById(
                    "movimentacaoQuantidade"
                );


            // LIMPAR ERRO ANTERIOR
            if (erroMovimentacao) {
                erroMovimentacao.textContent = "";
            }


            const produtoId =
                selectProduto.value;

            const operacao =
                selectTipo.value;

            const quantidade =
                Number(
                    inputQuantidade.value
                );


            // ==============================
            // VALIDAR PRODUTO
            // ==============================

            if (!produtoId) {

                if (erroMovimentacao) {
                    erroMovimentacao.textContent =
                        "Selecione um produto.";
                }

                return;
            }


            // ==============================
            // VALIDAR QUANTIDADE
            // ==============================

            if (
                !Number.isInteger(quantidade) ||
                quantidade <= 0
            ) {

                if (erroMovimentacao) {
                    erroMovimentacao.textContent =
                        "Informe uma quantidade maior que zero.";
                }

                return;
            }


            // ==============================
            // VERIFICAR ESTOQUE DISPONÍVEL
            // ==============================

            const opcaoSelecionada =
                selectProduto.options[
                    selectProduto.selectedIndex
                ];


            const estoqueDisponivel =
                Number(
                    opcaoSelecionada.dataset.quantidade
                );


            if (
                operacao === "remover" &&
                quantidade > estoqueDisponivel
            ) {

                if (erroMovimentacao) {
                    erroMovimentacao.textContent =
                        "Não é possível realizar uma saída maior que a quantidade disponível em estoque.";
                }

                return;
            }


            // ==============================
            // REGISTRAR MOVIMENTAÇÃO
            // ==============================

            try {

                const resposta =
                    await fetch(
                        `/api/produtos/${produtoId}/quantidade`,
                        {
                            method: "PATCH",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                operacao:
                                    operacao,

                                quantidade:
                                    quantidade
                            })
                        }
                    );


                const resultado =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        resultado.erro ||
                        "Não foi possível registrar a movimentação."
                    );

                }


                // LIMPAR FORMULÁRIO
                inputQuantidade.value = "";


                if (erroMovimentacao) {
                    erroMovimentacao.textContent = "";
                }


                // ATUALIZAR PRODUTOS
                await carregarProdutosMovimentacao();
                await carregarMovimentacoesRecentes();

                // MENSAGEM DE SUCESSO
                mostrarMensagem(
                    resultado.mensagem,
                    "sucesso"
                );


            } catch (erro) {

                if (erroMovimentacao) {

                    erroMovimentacao.textContent =
                        erro.message;

                }

            }

        }
    );

}
async function carregarMovimentacoesRecentes() {

    const tabela =
        document.getElementById(
            "tabelaMovimentacoesRecentes"
        );

    const semMovimentacoes =
        document.getElementById(
            "semMovimentacoesRecentes"
        );


    // Só executa na página Movimentações
    if (!tabela) {
        return;
    }


    try {

        const resposta =
            await fetch(
                "/api/movimentacoes"
            );


        if (!resposta.ok) {

            throw new Error(
                "Não foi possível carregar as movimentações."
            );

        }


        const movimentacoes =
            await resposta.json();


        // PEGAR SOMENTE AS 5 MAIS RECENTES
        const recentes =
            movimentacoes.slice(0, 5);


        tabela.innerHTML = "";


        // ==============================
        // NENHUMA MOVIMENTAÇÃO
        // ==============================

        if (recentes.length === 0) {

            if (semMovimentacoes) {
                semMovimentacoes.style.display =
                    "block";
            }

            return;

        }


        if (semMovimentacoes) {
            semMovimentacoes.style.display =
                "none";
        }


        // ==============================
        // RENDERIZAR
        // ==============================

        recentes.forEach(
            movimentacao => {

                const linha =
                    document.createElement(
                        "tr"
                    );


                const entrada =
                    movimentacao.tipo ===
                    "entrada";


                const tipoTexto =
                    entrada
                        ? "Entrada"
                        : "Saída";


                const tipoClasse =
                    entrada
                        ? "entrada"
                        : "saida";


                const sinalQuantidade =
                    entrada
                        ? "+"
                        : "-";


                const data =
                    new Date(
                        movimentacao.data_hora
                            .replace(
                                " ",
                                "T"
                            )
                    );


                const dataFormatada =
                    data.toLocaleString(
                        "pt-BR",
                        {
                            day: "2-digit",
                            month: "2-digit",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit"
                        }
                    );


                linha.innerHTML = `

                    <td>
                        ${dataFormatada}
                    </td>


                    <td>
                        ${escaparHTML(
                            movimentacao.produto_nome
                        )}
                    </td>


                    <td>

                        <span
                            class="movimentacao-tipo ${tipoClasse}"
                        >
                            ${tipoTexto}
                        </span>

                    </td>


                    <td>

                        <span
                            class="movimentacao-quantidade ${tipoClasse}"
                        >
                            ${sinalQuantidade}${movimentacao.quantidade}
                        </span>

                    </td>

                    <td>
    ${
        movimentacao.usuario_nome
            ? escaparHTML(
                movimentacao.usuario_nome
            )
            : "—"
    }
</td>
                `;


                tabela.appendChild(
                    linha
                );

            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar movimentações recentes:",
            erro
        );

    }

}
if (
    document.getElementById(
        "tabelaMovimentacoesRecentes"
    )
) {

    // Carrega imediatamente ao abrir a página
    carregarMovimentacoesRecentes();


    // Atualiza automaticamente a cada 5 segundos
    setInterval(
        carregarMovimentacoesRecentes,
        5000
    );

}
// ==============================
// LOGOUT
// ==============================

const btnLogout =
    document.getElementById("btnLogout");

if (btnLogout) {

    btnLogout.addEventListener(
        "click",
        async () => {

            try {

                const resposta =
                    await fetch(
                        "/api/logout",
                        {
                            method: "POST"
                        }
                    );

                const resultado =
                    await resposta.json();

                if (!resposta.ok) {
                    throw new Error(
                        resultado.erro ||
                        "Não foi possível sair da conta."
                    );
                }

                // Sessão encerrada.
                // Volta para a tela de login.
                window.location.href =
                    "/login";

            } catch (erro) {

                console.error(
                    "Erro ao realizar logout:",
                    erro
                );

                mostrarMensagem(
                    erro.message,
                    "erro"
                );

            }

        }
    );

}
// ==============================
// USUÁRIOS
// ==============================

async function carregarUsuarios() {

    const tabela =
        document.getElementById(
            "tabelaUsuarios"
        );

    const semUsuarios =
        document.getElementById(
            "semUsuarios"
        );


    if (!tabela) {
        return;
    }


    try {

        const resposta =
            await fetch(
                "/api/usuarios"
            );

        const usuarios =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                usuarios.erro ||
                "Não foi possível carregar os usuários."
            );

        }


        tabela.innerHTML = "";


        if (usuarios.length === 0) {

            if (semUsuarios) {
                semUsuarios.style.display =
                    "block";
            }

            return;

        }


        if (semUsuarios) {
            semUsuarios.style.display =
                "none";
        }


        usuarios.forEach(
            usuario => {

                const linha =
                    document.createElement(
                        "tr"
                    );


                linha.innerHTML = `

                    <td>
                        <div class="usuario-identificacao">

                            <div class="usuario-avatar">
                                ${escaparHTML(
                                    usuario.nome
                                        .charAt(0)
                                        .toUpperCase()
                                )}
                            </div>

                            <strong>
                                ${escaparHTML(
                                    usuario.nome
                                )}
                            </strong>

                        </div>
                    </td>


                    <td>
                        ${escaparHTML(
                            usuario.email
                        )}
                    </td>


                    <td>
                        <span
                            class="usuario-perfil ${
                                usuario.perfil ===
                                "Administrador"
                                    ? "administrador"
                                    : "funcionario"
                            }"
                        >
                            ${escaparHTML(
                                usuario.perfil
                            )}
                        </span>
                    </td>


                    <td>
                        <div class="usuario-acoes">

                            <button
    type="button"
    class="btn-editar"
    title="Editar usuário"
    onclick="abrirEdicaoUsuario(
        ${usuario.id},
        '${escaparHTML(usuario.nome)}',
        '${escaparHTML(usuario.email)}',
        ${usuario.perfil_id}
    )"
>
    ✏️
</button>
<button
    type="button"
    class="btn-excluir"
    title="Excluir usuário"
    onclick="abrirExclusaoUsuario(
        ${usuario.id},
        '${escaparHTML(usuario.nome)}'
    )"
>
    🗑️
</button>

                        </div>
                    </td>

                `;


                tabela.appendChild(
                    linha
                );

            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar usuários:",
            erro
        );

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}


if (
    document.getElementById(
        "tabelaUsuarios"
    )
) {

    carregarUsuarios();
    carregarPerfisUsuario();
}
// ==============================
// MODAL NOVO USUÁRIO
// ==============================

const btnNovoUsuario =
    document.getElementById("btnNovoUsuario");

const modalNovoUsuario =
    document.getElementById("modalNovoUsuario");

const btnFecharNovoUsuario =
    document.getElementById("btnFecharNovoUsuario");

const btnCancelarNovoUsuario =
    document.getElementById("btnCancelarNovoUsuario");

const formNovoUsuario =
    document.getElementById("formNovoUsuario");

const erroNovoUsuario =
    document.getElementById("erroNovoUsuario");


function abrirModalNovoUsuario() {

    if (!modalNovoUsuario) {
        return;
    }

    // Limpa o formulário ao abrir
    if (formNovoUsuario) {
        formNovoUsuario.reset();
    }

    // Limpa mensagens anteriores
    if (erroNovoUsuario) {
        erroNovoUsuario.textContent = "";
    }

    modalNovoUsuario.style.display = "flex";

    const campoNome =
        document.getElementById("novoUsuarioNome");

    if (campoNome) {
        campoNome.focus();
    }
}


function fecharModalNovoUsuario() {

    if (!modalNovoUsuario) {
        return;
    }

    modalNovoUsuario.style.display = "none";

    if (formNovoUsuario) {
        formNovoUsuario.reset();
    }

    if (erroNovoUsuario) {
        erroNovoUsuario.textContent = "";
    }
}


// BOTÃO + NOVO USUÁRIO
if (btnNovoUsuario) {

    btnNovoUsuario.addEventListener(
        "click",
        abrirModalNovoUsuario
    );

}


// BOTÃO X
if (btnFecharNovoUsuario) {

    btnFecharNovoUsuario.addEventListener(
        "click",
        fecharModalNovoUsuario
    );

}


// BOTÃO CANCELAR
if (btnCancelarNovoUsuario) {

    btnCancelarNovoUsuario.addEventListener(
        "click",
        fecharModalNovoUsuario
    );

}


// CLIQUE FORA DO MODAL
if (modalNovoUsuario) {

    modalNovoUsuario.addEventListener(
        "click",
        (evento) => {

            if (
                evento.target ===
                modalNovoUsuario
            ) {

                fecharModalNovoUsuario();

            }

        }
    );

}
// ==============================
// CADASTRAR NOVO USUÁRIO
// ==============================

if (formNovoUsuario) {

    formNovoUsuario.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();


            const campoNome =
                document.getElementById(
                    "novoUsuarioNome"
                );

            const campoEmail =
                document.getElementById(
                    "novoUsuarioEmail"
                );

            const campoSenha =
                document.getElementById(
                    "novoUsuarioSenha"
                );

            const campoPerfil =
                document.getElementById(
                    "novoUsuarioPerfil"
                );


            const nome =
                campoNome.value.trim();

            const email =
                campoEmail.value.trim();

            const senha =
                campoSenha.value;

            const perfilId =
                Number(campoPerfil.value);


            // Limpa erro anterior
            if (erroNovoUsuario) {
                erroNovoUsuario.textContent = "";
            }


            // ==============================
            // VALIDAÇÕES
            // ==============================

            if (
                !nome ||
                !email ||
                !senha ||
                !perfilId
            ) {

                if (erroNovoUsuario) {
                    erroNovoUsuario.textContent =
                        "Preencha todos os campos.";
                }

                return;
            }


            if (senha.length < 6) {

                if (erroNovoUsuario) {
                    erroNovoUsuario.textContent =
                        "A senha deve possuir pelo menos 6 caracteres.";
                }

                return;
            }


            try {

                const resposta =
                    await fetch(
                        "/api/usuarios",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                nome: nome,
                                email: email,
                                senha: senha,
                                perfil_id: perfilId
                            })
                        }
                    );


                const resultado =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        resultado.erro ||
                        "Não foi possível cadastrar o usuário."
                    );

                }


                // Fecha e limpa o modal
                fecharModalNovoUsuario();


                // Atualiza a tabela sem F5
                await carregarUsuarios();


                // Feedback
                mostrarMensagem(
                    resultado.mensagem,
                    "sucesso"
                );


            } catch (erro) {

                if (erroNovoUsuario) {

                    erroNovoUsuario.textContent =
                        erro.message;

                }

            }

        }
    );

}
// ==============================
// CARREGAR PERFIS
// ==============================

async function carregarPerfisUsuario() {

    const selectPerfil =
        document.getElementById(
            "novoUsuarioPerfil"
        );

    if (!selectPerfil) {
        return;
    }

    try {

        const resposta =
            await fetch("/api/perfis");

        const perfis =
            await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                perfis.erro ||
                "Não foi possível carregar os perfis."
            );
        }

        selectPerfil.innerHTML = `
            <option value="">
                Selecione um perfil
            </option>
        `;

        perfis.forEach(
            perfil => {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    perfil.id;

                option.textContent =
                    perfil.nome;

                selectPerfil.appendChild(
                    option
                );

            }
        );

    } catch (erro) {

        console.error(
            "Erro ao carregar perfis:",
            erro
        );

        mostrarMensagem(
            erro.message,
            "erro"
        );

    }

}
// ==============================
// EDITAR USUÁRIO
// ==============================

const modalEditarUsuario =
    document.getElementById("modalEditarUsuario");

const formEditarUsuario =
    document.getElementById("formEditarUsuario");

const btnFecharEditarUsuario =
    document.getElementById("btnFecharEditarUsuario");

const btnCancelarEditarUsuario =
    document.getElementById("btnCancelarEditarUsuario");

const erroEditarUsuario =
    document.getElementById("erroEditarUsuario");


// ==============================
// CARREGAR PERFIS DA EDIÇÃO
// ==============================

async function carregarPerfisEdicaoUsuario(
    perfilSelecionado
) {

    const select =
        document.getElementById(
            "editarUsuarioPerfil"
        );

    if (!select) {
        return;
    }

    try {

        const resposta =
            await fetch("/api/perfis");

        const perfis =
            await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                perfis.erro ||
                "Não foi possível carregar os perfis."
            );
        }

        select.innerHTML = `
            <option value="">
                Selecione um perfil
            </option>
        `;

        perfis.forEach(
            perfil => {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    perfil.id;

                option.textContent =
                    perfil.nome;

                select.appendChild(
                    option
                );

            }
        );

        select.value =
            String(perfilSelecionado);

    } catch (erro) {

        if (erroEditarUsuario) {
            erroEditarUsuario.textContent =
                erro.message;
        }

    }

}


// ==============================
// ABRIR EDIÇÃO
// ==============================

async function abrirEdicaoUsuario(
    id,
    nome,
    email,
    perfilId
) {

    if (!modalEditarUsuario) {
        return;
    }

    document.getElementById(
        "editarUsuarioId"
    ).value = id;

    document.getElementById(
        "editarUsuarioNome"
    ).value = nome;

    document.getElementById(
        "editarUsuarioEmail"
    ).value = email;

    if (erroEditarUsuario) {
        erroEditarUsuario.textContent = "";
    }

    await carregarPerfisEdicaoUsuario(
        perfilId
    );

    modalEditarUsuario.style.display =
        "flex";

}


// ==============================
// FECHAR EDIÇÃO
// ==============================

function fecharModalEditarUsuario() {

    if (!modalEditarUsuario) {
        return;
    }

    modalEditarUsuario.style.display =
        "none";

    if (formEditarUsuario) {
        formEditarUsuario.reset();
    }

    if (erroEditarUsuario) {
        erroEditarUsuario.textContent = "";
    }

}


// X
if (btnFecharEditarUsuario) {

    btnFecharEditarUsuario.addEventListener(
        "click",
        fecharModalEditarUsuario
    );

}


// CANCELAR
if (btnCancelarEditarUsuario) {

    btnCancelarEditarUsuario.addEventListener(
        "click",
        fecharModalEditarUsuario
    );

}


// CLIQUE FORA
if (modalEditarUsuario) {

    modalEditarUsuario.addEventListener(
        "click",
        (evento) => {

            if (
                evento.target ===
                modalEditarUsuario
            ) {
                fecharModalEditarUsuario();
            }

        }
    );

}


// ==============================
// SALVAR ALTERAÇÕES
// ==============================

if (formEditarUsuario) {

    formEditarUsuario.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();

            const id =
                document.getElementById(
                    "editarUsuarioId"
                ).value;

            const nome =
                document.getElementById(
                    "editarUsuarioNome"
                ).value.trim();

            const email =
                document.getElementById(
                    "editarUsuarioEmail"
                ).value.trim();

            const perfilId =
                Number(
                    document.getElementById(
                        "editarUsuarioPerfil"
                    ).value
                );


            if (erroEditarUsuario) {
                erroEditarUsuario.textContent = "";
            }


            if (
                !nome ||
                !email ||
                !perfilId
            ) {

                if (erroEditarUsuario) {
                    erroEditarUsuario.textContent =
                        "Preencha todos os campos.";
                }

                return;
            }


            try {

                const resposta =
                    await fetch(
                        `/api/usuarios/${id}`,
                        {
                            method: "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                nome: nome,
                                email: email,
                                perfil_id: perfilId
                            })
                        }
                    );


                const resultado =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        resultado.erro ||
                        "Não foi possível atualizar o usuário."
                    );

                }


                fecharModalEditarUsuario();

                await carregarUsuarios();


                mostrarMensagem(
                    resultado.mensagem,
                    "sucesso"
                );


            } catch (erro) {

                if (erroEditarUsuario) {
                    erroEditarUsuario.textContent =
                        erro.message;
                }

            }

        }
    );

}
// ==============================
// EXCLUIR USUÁRIO
// ==============================

const modalExcluirUsuario =
    document.getElementById("modalExcluirUsuario");

const btnFecharExcluirUsuario =
    document.getElementById("btnFecharExcluirUsuario");

const btnCancelarExcluirUsuario =
    document.getElementById("btnCancelarExcluirUsuario");

const btnConfirmarExcluirUsuario =
    document.getElementById("btnConfirmarExcluirUsuario");

const erroExcluirUsuario =
    document.getElementById("erroExcluirUsuario");


// ==============================
// ABRIR MODAL
// ==============================

function abrirExclusaoUsuario(
    id,
    nome
) {

    if (!modalExcluirUsuario) {
        return;
    }

    const campoId =
        document.getElementById(
            "excluirUsuarioId"
        );

    const campoNome =
        document.getElementById(
            "excluirUsuarioNome"
        );


    if (campoId) {
        campoId.value = id;
    }

    if (campoNome) {
        campoNome.textContent = nome;
    }

    if (erroExcluirUsuario) {
        erroExcluirUsuario.textContent = "";
    }

    modalExcluirUsuario.style.display =
        "flex";
}


// ==============================
// FECHAR MODAL
// ==============================

function fecharModalExcluirUsuario() {

    if (!modalExcluirUsuario) {
        return;
    }

    modalExcluirUsuario.style.display =
        "none";

    const campoId =
        document.getElementById(
            "excluirUsuarioId"
        );

    const campoNome =
        document.getElementById(
            "excluirUsuarioNome"
        );

    if (campoId) {
        campoId.value = "";
    }

    if (campoNome) {
        campoNome.textContent = "";
    }

    if (erroExcluirUsuario) {
        erroExcluirUsuario.textContent = "";
    }
}


// ==============================
// FORMAS DE FECHAR
// ==============================

// X
if (btnFecharExcluirUsuario) {

    btnFecharExcluirUsuario.addEventListener(
        "click",
        fecharModalExcluirUsuario
    );

}


// CANCELAR
if (btnCancelarExcluirUsuario) {

    btnCancelarExcluirUsuario.addEventListener(
        "click",
        fecharModalExcluirUsuario
    );

}


// CLIQUE FORA
if (modalExcluirUsuario) {

    modalExcluirUsuario.addEventListener(
        "click",
        (evento) => {

            if (
                evento.target ===
                modalExcluirUsuario
            ) {
                fecharModalExcluirUsuario();
            }

        }
    );

}


// ==============================
// CONFIRMAR EXCLUSÃO
// ==============================

if (btnConfirmarExcluirUsuario) {

    btnConfirmarExcluirUsuario.addEventListener(
        "click",
        async () => {

            const campoId =
                document.getElementById(
                    "excluirUsuarioId"
                );

            if (!campoId) {
                return;
            }

            const usuarioId =
                campoId.value;


            if (!usuarioId) {
                return;
            }


            if (erroExcluirUsuario) {
                erroExcluirUsuario.textContent = "";
            }


            try {

                const resposta =
                    await fetch(
                        `/api/usuarios/${usuarioId}`,
                        {
                            method: "DELETE"
                        }
                    );


                const resultado =
                    await resposta.json();


                if (!resposta.ok) {

                    throw new Error(
                        resultado.erro ||
                        "Não foi possível excluir o usuário."
                    );

                }


                fecharModalExcluirUsuario();

                await carregarUsuarios();


                mostrarMensagem(
                    resultado.mensagem,
                    "sucesso"
                );


            } catch (erro) {

                if (erroExcluirUsuario) {

                    erroExcluirUsuario.textContent =
                        erro.message;

                }

            }

        }
    );

}
// ==============================
// GRÁFICO DO DASHBOARD
// ==============================

async function carregarGraficoDashboard() {

    const grafico =
        document.getElementById(
            "graficoMovimentacoes"
        );

    if (!grafico) {
        return;
    }

    try {

        const resposta =
            await fetch("/api/movimentacoes");

        const movimentacoes =
            await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                movimentacoes.erro ||
                "Não foi possível carregar o gráfico."
            );
        }


        // ==============================
        // CRIAR OS ÚLTIMOS 7 DIAS
        // ==============================

        const dias = [];

        const hoje = new Date();

        hoje.setHours(0, 0, 0, 0);


        for (let i = 6; i >= 0; i--) {

            const data = new Date(hoje);

            data.setDate(
                hoje.getDate() - i
            );

            const ano =
                data.getFullYear();

            const mes =
                String(
                    data.getMonth() + 1
                ).padStart(2, "0");

            const dia =
                String(
                    data.getDate()
                ).padStart(2, "0");


            dias.push({
                chave:
                    `${ano}-${mes}-${dia}`,

                label:
                    `${dia}/${mes}`,

                entradas: 0,

                saidas: 0
            });

        }


        // ==============================
        // AGRUPAR MOVIMENTAÇÕES
        // ==============================

        movimentacoes.forEach(
            movimentacao => {

                if (!movimentacao.data_hora) {
                    return;
                }


                // SQLite:
                // 2026-09-23 10:30:00

                const dataMovimentacao =
                    movimentacao.data_hora
                        .substring(0, 10);


                const diaEncontrado =
                    dias.find(
                        item =>
                            item.chave ===
                            dataMovimentacao
                    );


                if (!diaEncontrado) {
                    return;
                }


                const quantidade =
                    Number(
                        movimentacao.quantidade
                    ) || 0;


                if (
                    movimentacao.tipo ===
                    "entrada"
                ) {

                    diaEncontrado.entradas +=
                        quantidade;

                } else if (
                    movimentacao.tipo ===
                    "saida"
                ) {

                    diaEncontrado.saidas +=
                        quantidade;

                }

            }
        );

// ==============================
// RESUMO DOS ÚLTIMOS 7 DIAS
// ==============================

let totalEntradasPeriodo = 0;
let totalSaidasPeriodo = 0;

let quantidadeEntradasPeriodo = 0;
let quantidadeSaidasPeriodo = 0;


// Somar quantidades movimentadas
dias.forEach(
    dia => {

        totalEntradasPeriodo +=
            dia.entradas;

        totalSaidasPeriodo +=
            dia.saidas;

    }
);


// Contar movimentações do período
movimentacoes.forEach(
    movimentacao => {

        if (!movimentacao.data_hora) {
            return;
        }

        const dataMovimentacao =
            movimentacao.data_hora
                .substring(0, 10);


        const estaNoPeriodo =
            dias.some(
                dia =>
                    dia.chave ===
                    dataMovimentacao
            );


        if (!estaNoPeriodo) {
            return;
        }


        if (
            movimentacao.tipo ===
            "entrada"
        ) {

            quantidadeEntradasPeriodo++;

        } else if (
            movimentacao.tipo ===
            "saida"
        ) {

            quantidadeSaidasPeriodo++;

        }

    }
);


// ==============================
// ATUALIZAR RESUMO
// ==============================

const periodoTotalEntradas =
    document.getElementById(
        "periodoTotalEntradas"
    );

const periodoTotalSaidas =
    document.getElementById(
        "periodoTotalSaidas"
    );

const periodoQuantidadeEntradas =
    document.getElementById(
        "periodoQuantidadeEntradas"
    );

const periodoQuantidadeSaidas =
    document.getElementById(
        "periodoQuantidadeSaidas"
    );


if (periodoTotalEntradas) {

    periodoTotalEntradas.textContent =
        totalEntradasPeriodo;

}


if (periodoTotalSaidas) {

    periodoTotalSaidas.textContent =
        totalSaidasPeriodo;

}


if (periodoQuantidadeEntradas) {

    periodoQuantidadeEntradas.textContent =
        quantidadeEntradasPeriodo === 1
            ? "1 movimentação"
            : `${quantidadeEntradasPeriodo} movimentações`;

}


if (periodoQuantidadeSaidas) {

    periodoQuantidadeSaidas.textContent =
        quantidadeSaidasPeriodo === 1
            ? "1 movimentação"
            : `${quantidadeSaidasPeriodo} movimentações`;

}
        // ==============================
        // MAIOR VALOR
        // ==============================

        const valores = [];

        dias.forEach(
            dia => {
                valores.push(
                    dia.entradas,
                    dia.saidas
                );
            }
        );


        const maiorValor =
            Math.max(
                ...valores,
                1
            );


        // ==============================
        // MONTAR GRÁFICO
        // ==============================

        grafico.innerHTML = "";


        dias.forEach(
            dia => {

                const coluna =
                    document.createElement(
                        "div"
                    );

                coluna.className =
                    "grafico-coluna";


                const alturaEntrada =
                    dia.entradas === 0
                        ? 0
                        : (
                            dia.entradas /
                            maiorValor
                        ) * 100;


                const alturaSaida =
                    dia.saidas === 0
                        ? 0
                        : (
                            dia.saidas /
                            maiorValor
                        ) * 100;


                coluna.innerHTML = `

                    <div class="grafico-barras">

                        <div
                            class="grafico-barra entrada"
                            style="
                                height:
                                ${alturaEntrada}%;
                            "
                            title="
                                Entradas:
                                ${dia.entradas}
                            "
                        ></div>


                        <div
                            class="grafico-barra saida"
                            style="
                                height:
                                ${alturaSaida}%;
                            "
                            title="
                                Saídas:
                                ${dia.saidas}
                            "
                        ></div>

                    </div>


                    <span class="grafico-data">
                        ${dia.label}
                    </span>

                `;


                grafico.appendChild(
                    coluna
                );

            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar gráfico:",
            erro
        );

        grafico.innerHTML = `
            <p class="dashboard-vazio">
                Não foi possível carregar o gráfico.
            </p>
        `;

    }

}


// Carrega somente quando estiver no Dashboard
if (
    document.getElementById(
        "graficoMovimentacoes"
    )
) {

    carregarGraficoDashboard();

}