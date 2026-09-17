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

btnNovaCategoria.addEventListener(
    "click",
    abrirNovaCategoria
);

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

        atualizarDashboard();

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


// ==============================
// RENDERIZAR TABELA DE PRODUTOS
// ==============================

function renderizarProdutos() {

    const termo =
        pesquisa.value
            .toLowerCase()
            .trim();

    semProdutos.style.display = "none";

    const produtosFiltrados =
        produtos.filter(produto => {

            return (
                produto.nome
                    .toLowerCase()
                    .includes(termo) ||

                produto.sku
                    .toLowerCase()
                    .includes(termo)
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
                ${escaparHTML(produto.sku)}
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

                <span class="status ${statusClasse}">
                    ${statusTexto}
                </span>

            </td>

            <td>

                <button
                    class="btn-editar"
                    onclick="abrirEdicao(${produto.id})"
                    title="Editar produto"
                >
                    ✏️
                </button>

                <button
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


            await carregarProdutos();


        } catch (erro) {

            mostrarMensagem(
                erro.message,
                "erro"
            );

        }

    }
);


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

async function excluirProduto(id) {

    const confirmar =
        confirm(
            "Tem certeza que deseja excluir este produto?"
        );


    if (!confirmar) {
        return;
    }


    try {

        const resposta =
            await fetch(
                `/api/produtos/${id}`,
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


        mostrarMensagem(
            resultado.mensagem,
            "sucesso"
        );


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
// PESQUISA DE PRODUTOS
// ==============================

pesquisa.addEventListener(
    "input",
    renderizarProdutos
);


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


// ==============================
// ABRIR EDIÇÃO
// ==============================

function abrirEdicao(id) {

    const produto =
        produtos.find(
            produto => produto.id === id
        );


    if (!produto) {
        return;
    }


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

        lista.innerHTML = "";


        categorias.forEach(
            categoria => {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "categoria-item";


                item.innerHTML = `

                    <span>
                        ${escaparHTML(
                            categoria.nome
                        )}
                    </span>

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


                lista.appendChild(item);

            }
        );


        // ==============================
        // SELECT DO CADASTRO
        // ==============================

        selectCategoria.innerHTML = `

            <option value="">
                Selecione uma categoria
            </option>

        `;


        // ==============================
        // SELECT DA EDIÇÃO
        // ==============================

        selectEditarCategoria.innerHTML = `

            <option value="">
                Selecione uma categoria
            </option>

        `;


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


                selectCategoria.appendChild(
                    opcaoCadastro
                );


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
        );


    } catch (erro) {

        mostrarMensagem(
            "Não foi possível carregar as categorias.",
            "erro"
        );

    }

}


carregarCategorias();


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
            await fetch(
                "/api/categorias"
            );


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


        const novoNome =
            prompt(
                "Digite o novo nome da categoria:",
                categoria.nome
            );


        if (novoNome === null) {
            return;
        }


        const nome =
            novoNome.trim();


        if (!nome) {

            mostrarMensagem(
                "Digite um nome para a categoria.",
                "erro"
            );

            return;

        }


        const respostaEdicao =
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
            await respostaEdicao.json();


        if (!respostaEdicao.ok) {

            throw new Error(
                resultado.erro
            );

        }


        mostrarMensagem(
            resultado.mensagem,
            "sucesso"
        );


        await carregarCategorias();

        await carregarProdutos();


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

async function excluirCategoria(id) {

    try {

        const respostaCategorias =
            await fetch(
                "/api/categorias"
            );


        const categorias =
            await respostaCategorias.json();


        const categoria =
            categorias.find(
                categoria =>
                    categoria.id === id
            );


        if (!categoria) {
            return;
        }


        const confirmar =
            confirm(
                `Tem certeza que deseja excluir a categoria "${categoria.nome}"?`
            );


        if (!confirmar) {
            return;
        }


        const resposta =
            await fetch(
                `/api/categorias/${id}`,
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

async function carregarMovimentacoes() {

    try {

        const resposta =
            await fetch(
                "/api/movimentacoes"
            );


        const movimentacoes =
            await resposta.json();


        // ==============================
        // CONTADORES DE ENTRADAS E SAÍDAS
        // ==============================

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


        totalEntradas.textContent =
            quantidadeEntradas;


        totalSaidas.textContent =
            quantidadeSaidas;


        // ==============================
        // ELEMENTOS DO HISTÓRICO
        // ==============================

        const tabela =
            document.getElementById(
                "tabelaMovimentacoes"
            );


        const semMovimentacoes =
            document.getElementById(
                "semMovimentacoes"
            );


        // ==============================
        // FILTROS
        // ==============================

        const termoProduto =
            filtroProduto.value
                .toLowerCase()
                .trim();


        const tipoSelecionado =
            filtroTipo.value;


        const dataSelecionada =
            filtroData.value;


        // ==============================
        // APLICAR FILTROS
        // ==============================

        const movimentacoesFiltradas =
            movimentacoes.filter(
                movimentacao => {

                    const correspondeProduto =
                        movimentacao.produto_nome
                            .toLowerCase()
                            .includes(
                                termoProduto
                            );


                    const correspondeTipo =
                        tipoSelecionado ===
                            "todos" ||
                        movimentacao.tipo ===
                            tipoSelecionado;


                    let correspondeData =
                        true;


                    if (
                        dataSelecionada
                    ) {

                        correspondeData =
                            movimentacao.data_hora
                                .startsWith(
                                    dataSelecionada
                                );

                    }


                    return (
                        correspondeProduto &&
                        correspondeTipo &&
                        correspondeData
                    );

                }
            );


        // ==============================
        // LIMPAR TABELA
        // ==============================

        tabela.innerHTML = "";


        // ==============================
        // NENHUMA MOVIMENTAÇÃO
        // ==============================

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


        // ==============================
        // RENDERIZAR MOVIMENTAÇÕES
        // ==============================

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


                linha.innerHTML = `

                    <td>
                        ${escaparHTML(
                            movimentacao.produto_nome
                        )}
                    </td>

                    <td>
                        <span class="${tipoClasse}">
                            ${tipoTexto}
                        </span>
                    </td>

                    <td>
                        ${movimentacao.quantidade}
                    </td>

                    <td>
                        ${dataFormatada}
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


// ==============================
// FILTROS DO HISTÓRICO
// ==============================

filtroProduto.addEventListener(
    "input",
    carregarMovimentacoes
);


filtroTipo.addEventListener(
    "change",
    carregarMovimentacoes
);


filtroData.addEventListener(
    "change",
    carregarMovimentacoes
);


btnLimparFiltros.addEventListener(
    "click",
    () => {

        filtroProduto.value = "";

        filtroTipo.value = "todos";

        filtroData.value = "";

        carregarMovimentacoes();

    }
);


// ==============================
// INICIALIZAÇÃO
// ==============================

window.addEventListener(
    "load",
    () => {
        carregarProdutos();
        carregarMovimentacoes();
        verificarSessao();
    }
);
const btnLogout = document.getElementById("btnLogout");

if (btnLogout) {

    btnLogout.addEventListener(
        "click",
        async function () {

            try {

                const resposta = await fetch(
                    "/api/logout",
                    {
                        method: "POST"
                    }
                );

                if (resposta.ok) {

                    window.location.href = "/login";

                }

            } catch (erro) {

                console.error(
                    "Erro ao realizar logout:",
                    erro
                );

            }

        }
    );

}
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