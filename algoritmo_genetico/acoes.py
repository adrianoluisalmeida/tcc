from random import random
import matplotlib.pyplot as plt

class Produto():
    def __init__(self, nome, risco, rentabilidade):
        self.nome = nome
        self.risco = risco
        self.rentabilidade = rentabilidade
        
    
class Individuo():
    def __init__(self, riscos, rentabilidades, limite_riscos, geracao=0):
        self.riscos = riscos
        self.rentabilidades = rentabilidades
        self.limite_riscos = limite_riscos
        self.nota_avaliacao = 0 #cada um vai ter uma nota para comparar se é bom ou não, em relação aos outros #singifica, somatório das rentabilidades
        self.risco_usado = 0 #somatório do risco utilizado
        self.geracao = geracao
        self.cromossomo = []
        self.total = 0
        
        #inicialização aleatória
        for i in range(len(riscos)):
            if random() < 0.5: #50% probabilidade de por [1 ou 0]
                self.cromossomo.append("0")
            else:
                self.cromossomo.append("1")
                
            
                
    def avaliacao(self):
        nota = 0
        soma_riscos = 0
        for i in range(len(self.cromossomo)):
            if self.cromossomo[i] == "1":
                nota += self.rentabilidades[i]
                soma_riscos += self.riscos[i]
                
        if soma_riscos > self.limite_riscos: #limite riscos
            nota = 1 #importante: não usar valores negativos para não excluir os valores ruins, somente rebaixa-los
            
        self.nota_avaliacao = nota
        self.risco_usado = soma_riscos
    
    
    def crossover(self, outro_individuo):
        corte = round(random() * len(self.cromossomo)) #random de 0 a 1; exemplo 0,45 * len(cromossomo)= 6,13414
        
        filho1 = outro_individuo.cromossomo[0:corte]+self.cromossomo[corte::] #corte:: => indica que é tudo para frente do corte
        filho2 = self.cromossomo[0:corte] + outro_individuo.cromossomo[corte::]
        
        
        filhos = [Individuo(self.riscos, self.rentabilidades, self.limite_riscos, self.geracao+1),
                  Individuo(self.riscos, self.rentabilidades, self.limite_riscos, self.geracao+1)]
        
        filhos[0].cromossomo = filho1
        filhos[1].cromossomo = filho2
        
        return filhos
    
    def mutacao(self, taxa_de_mutacao):
        #print("Antes %s" % self.cromossomo)
        for i in range(len(self.cromossomo)):
            if random() < taxa_de_mutacao:
                if self.cromossomo[i] == '1':
                    self.cromossomo[i] = '0'
                else:
                    self.cromossomo[i] = '1'
                    
        #print("Depois %s" % self.cromossomo)
        return self
    
class AlgoritmoGenetico():
    def __init__(self, tamanho_populacao):
        self.tamanho_populacao = tamanho_populacao
        self.populacao = [] #vai armazenar novos objetos da classe individuos
        self.geracao = 0
        self.melhor_solucao = 0
        self.lista_solucoes = []
        
    def inicializa_populacao(self, riscos, rentabilidades, limite_riscos):
        for i in range(self.tamanho_populacao):
            self.populacao.append(Individuo(riscos, rentabilidades, limite_riscos))
        self.melhor_solucao = self.populacao[0]
        
    def orderna_populacao(self):
        self.populacao = sorted(self.populacao, key = lambda populacao: populacao.nota_avaliacao, reverse = True)
        
    def melhor_individuo(self, individuo):
        if individuo.nota_avaliacao > self.melhor_solucao.nota_avaliacao:
            self.melhor_solucao = individuo
            
    def soma_avaliacoes(self):
        soma = 0
        for individuo in self.populacao:
            soma += individuo.nota_avaliacao
        
        return soma
    
    def seleciona_pai(self, soma_avaliacao):
        pai = -1
        valor_sorteado = random() * soma_avaliacao
        soma = 0
        i = 0
        while i < len(self.populacao) and soma < valor_sorteado:
            soma += self.populacao[i].nota_avaliacao
            pai += 1
            i += 1
            
        return pai
    
    def visualiza_geracao(self):
        melhor = self.populacao[0]
        print("G:%s -> Soma Rentabilidade: %s Risco: %s Cromossomo: %s" % (melhor.geracao, melhor.nota_avaliacao, melhor.risco_usado, melhor.cromossomo))
            
        
    def resolver(self, taxa_mutacao, numero_geracoes, riscos, rentabilidades, limite_riscos):
        self.inicializa_populacao(riscos, rentabilidades, limite_riscos)
        
        for individuo in self.populacao:
            individuo.avaliacao()
    
        self.orderna_populacao()
        self.melhor_solucao = self.populacao[0]
        self.lista_solucoes.append(self.melhor_solucao.nota_avaliacao)
        
        self.visualiza_geracao()
        
        for geracao in range(numero_geracoes):
            soma_avaliacao = self.soma_avaliacoes()
            nova_populacao = []
            
            for individuo_gerados in range(0, self.tamanho_populacao, 2):
                pai1 = self.seleciona_pai(soma_avaliacao)
                pai2 = self.seleciona_pai(soma_avaliacao)
                
                
                #crossover
                filhos = self.populacao[pai1].crossover(self.populacao[pai2])
                
                #mutação
                nova_populacao.append(filhos[0].mutacao(taxa_mutacao))
                nova_populacao.append(filhos[1].mutacao(taxa_mutacao))
                
                
            self.populacao = list(nova_populacao)
            
            for individuo in self.populacao:
                individuo.avaliacao()
                
            self.orderna_populacao()
            self.visualiza_geracao()
            
            melhor = self.populacao[0]
            self.lista_solucoes.append(melhor.nota_avaliacao)
            self.melhor_individuo(melhor)
            
        print("\n== Melhor solução == \n G: %s\n Soma Rentabilidade: %s\n Risco: %s\n Cromossomo: %s\n" % (self.melhor_solucao.geracao, self.melhor_solucao.nota_avaliacao, self.melhor_solucao.risco_usado, self.melhor_solucao.cromossomo))
        
        return self.melhor_solucao.cromossomo
    
if __name__ == '__main__':
    #p1 = Produto("Iphone 6", 0.0000899, 2199.12)
    lista_produtos = []
    lista_produtos.append(Produto("ABEV3.SA", 0.246573, 0.298087))
    lista_produtos.append(Produto("AZUL4.SA", 0.397737, 0.410521))
    lista_produtos.append(Produto("B3SA3.SA", 0.342992, 0.250085))
    lista_produtos.append(Produto("BBAS3.SA", 0.398683, 0.236110))
    lista_produtos.append(Produto("BBDC4.SA", 0.356768, 0.197818))
    lista_produtos.append(Produto("BBSE3.SA", 0.301607, 0.217235))
    lista_produtos.append(Produto("BRAP4.SA", 0.420530, 0.157513))
    lista_produtos.append(Produto("BRDT3.SA", 0.398723, 0.467120))
    lista_produtos.append(Produto("BRFS3.SA", 0.320957, 0.141697))
    lista_produtos.append(Produto("BRKM5.SA", 0.409704, 0.278408))
    lista_produtos.append(Produto("BRML3.SA", 0.356767, 0.232817))
    lista_produtos.append(Produto("BTOW3.SA", 0.554952, 0.229370))
    lista_produtos.append(Produto("CCRO3.SA", 0.342414, 0.237620))
    lista_produtos.append(Produto("CIEL3.SA", 0.337954, 0.150095))
    
    

    #for produto in lista_produtos:
    #    print(produto.nome)
    riscos = []
    rentabilidades = []
    nomes = []
    
    for produto in lista_produtos:
        riscos.append(produto.risco)
        rentabilidades.append(produto.rentabilidade)
        nomes.append(produto.nome)
        
    quantidade_ativos = 5
    media_risco_ibov = 0.40568064553340555
    media_rentabilidade_ibov = 0.25318203628194313
    limite = media_risco_ibov*quantidade_ativos
    
    tamanho_populacao = 10
    taxa_mutacao = 0.01 #taxa de mutação
    numero_geracoes = 100 #numero máx de gerações  = critério de parada

    ag = AlgoritmoGenetico(tamanho_populacao)
    resultado = ag.resolver(taxa_mutacao, numero_geracoes, riscos, rentabilidades, limite)
    
    
    total_rentabilidade_carteira = 0
    total_risco_carteira = 0
    total_ativos_escolhidos = 0
    for i in range(len(lista_produtos)):
        if resultado[i] == '1':
            total_rentabilidade_carteira += lista_produtos[i].rentabilidade
            total_risco_carteira += lista_produtos[i].risco
            total_ativos_escolhidos += 1
            
            print("Ativo: %s Rentabilidade: %s" % (lista_produtos[i].nome, lista_produtos[i].rentabilidade))
            
    media_rentabilidade_carteira  = (total_rentabilidade_carteira/total_ativos_escolhidos)
    media_risco_carteira = (total_risco_carteira/total_ativos_escolhidos)
    
    print("\nRentabilidade média da carteira: %s" % media_rentabilidade_carteira)
    print("Risco médio da carteira: %s\n" % media_risco_carteira)
    
    print("\nRentabilidade média IBOV: %s" % media_rentabilidade_ibov)
    print("Risco médio da IBOV: %s\n" % media_risco_ibov)
    
    print("RENTABILIDADE DA CARTEIRA %.0f%%" % (((media_rentabilidade_carteira*100)/media_rentabilidade_ibov)-100))
    print("RISCO DA CARTEIRA %.0f%%" % (((media_risco_carteira*100)/media_risco_ibov)-100))
   
    plt.plot(ag.lista_solucoes)
    plt.title("Acompanhamento do somatório das rentabilidades dos ativos")
    plt.show();