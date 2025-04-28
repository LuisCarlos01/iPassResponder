"""
Módulo de Classificação de E-mails com Machine Learning

Este módulo implementa um classificador de e-mails simples usando
técnicas básicas de machine learning para melhorar a detecção de
palavras-chave e categorização de e-mails.
"""

import os
import pickle
import logging
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib

# Configurar logging
logger = logging.getLogger(__name__)

class EmailClassifier:
    """
    Classificador de e-mails que utiliza aprendizado de máquina para
    categorizar mensagens e melhorar a detecção de palavras-chave.
    """
    
    def __init__(self, model_file='models/email_classifier.pkl', threshold=0.6):
        """
        Inicializa o classificador de e-mails.
        
        Args:
            model_file (str): Caminho para arquivo do modelo treinado
            threshold (float): Limiar de confiança para classificação (0.0 a 1.0)
        """
        self.model_file = model_file
        self.threshold = threshold
        self.model = None
        self.classes = []
        self.is_trained = False
        
        # Tentar carregar modelo existente
        self.load_model()
    
    def load_model(self):
        """
        Carrega um modelo previamente treinado.
        
        Returns:
            bool: True se o modelo foi carregado com sucesso, False caso contrário
        """
        if os.path.exists(self.model_file):
            try:
                model_data = joblib.load(self.model_file)
                
                self.model = model_data.get('model')
                self.classes = model_data.get('classes', [])
                self.is_trained = True
                
                logger.info(f"Modelo carregado com {len(self.classes)} classes: {', '.join(self.classes)}")
                return True
                
            except Exception as e:
                logger.error(f"Erro ao carregar modelo: {str(e)}")
        
        logger.info("Nenhum modelo existente encontrado")
        return False
    
    def save_model(self):
        """
        Salva o modelo treinado.
        
        Returns:
            bool: True se o modelo foi salvo com sucesso, False caso contrário
        """
        if not self.is_trained or self.model is None:
            logger.warning("Tentativa de salvar modelo não treinado")
            return False
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
            
            # Preparar dados do modelo
            model_data = {
                'model': self.model,
                'classes': self.classes,
                'timestamp': datetime.now(),
                'version': '1.0'
            }
            
            # Salvar modelo
            joblib.dump(model_data, self.model_file)
            
            logger.info(f"Modelo salvo em {self.model_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {str(e)}")
            return False
    
    def train(self, texts, labels):
        """
        Treina o modelo com os dados fornecidos.
        
        Args:
            texts (list): Lista de textos para treinamento
            labels (list): Lista de rótulos correspondentes
            
        Returns:
            float: Acurácia do modelo após treinamento
        """
        if not texts or not labels or len(texts) != len(labels):
            logger.error("Dados de treinamento inválidos")
            return 0.0
        
        try:
            # Obter classes únicas
            self.classes = sorted(list(set(labels)))
            
            # Criar pipeline de pré-processamento e classificação
            self.model = Pipeline([
                ('vectorizer', TfidfVectorizer(
                    max_features=5000,
                    min_df=2,
                    max_df=0.85,
                    strip_accents='unicode',
                    lowercase=True,
                    ngram_range=(1, 2)
                )),
                ('classifier', MultinomialNB(alpha=0.1))
            ])
            
            # Dividir dados em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42
            )
            
            # Treinar modelo
            self.model.fit(X_train, y_train)
            
            # Avaliar o modelo
            accuracy = self.model.score(X_test, y_test)
            
            self.is_trained = True
            logger.info(f"Modelo treinado com acurácia de {accuracy:.2f} em {len(self.classes)} classes")
            
            # Salvar modelo
            self.save_model()
            
            return accuracy
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            self.is_trained = False
            return 0.0
    
    def predict(self, text):
        """
        Classifica um texto usando o modelo treinado.
        
        Args:
            text (str): Texto a ser classificado
            
        Returns:
            tuple: (classe_predita, confiança) ou (None, 0.0) se falhar
        """
        if not self.is_trained or not text:
            return None, 0.0
        
        try:
            # Obter probabilidades para cada classe
            proba = self.model.predict_proba([text])[0]
            
            # Obter índice da classe com maior probabilidade
            max_idx = np.argmax(proba)
            
            # Obter classe e confiança
            predicted_class = self.classes[max_idx]
            confidence = proba[max_idx]
            
            # Verificar se a confiança excede o limiar
            if confidence >= self.threshold:
                return predicted_class, confidence
            else:
                return None, confidence
                
        except Exception as e:
            logger.error(f"Erro ao classificar texto: {str(e)}")
            return None, 0.0
    
    def get_keywords_by_class(self, class_name, top_n=10):
        """
        Obtém as palavras-chave mais relevantes para uma classe específica.
        
        Args:
            class_name (str): Nome da classe
            top_n (int): Número de palavras-chave a retornar
            
        Returns:
            list: Lista de palavras-chave mais relevantes
        """
        if not self.is_trained or not class_name in self.classes:
            return []
        
        try:
            # Obter o vectorizer do pipeline
            vectorizer = self.model.named_steps['vectorizer']
            classifier = self.model.named_steps['classifier']
            
            # Obter o índice da classe
            class_idx = self.classes.index(class_name)
            
            # Obter os coeficientes do classificador para a classe
            if hasattr(classifier, 'feature_log_prob_'):
                # Para Naive Bayes
                class_features = classifier.feature_log_prob_[class_idx]
            else:
                # Fallback para outros classificadores
                class_features = classifier.coef_[class_idx] if hasattr(classifier, 'coef_') else []
            
            if len(class_features) == 0:
                return []
            
            # Obter recursos (palavras) do vectorizer
            feature_names = vectorizer.get_feature_names_out()
            
            # Ordenar por relevância
            top_indices = np.argsort(class_features)[-top_n:]
            
            # Obter palavras-chave
            return [feature_names[i] for i in top_indices]
            
        except Exception as e:
            logger.error(f"Erro ao obter palavras-chave: {str(e)}")
            return []
    
    def add_training_example(self, text, label, train_now=False):
        """
        Adiciona um novo exemplo de treinamento e opcionalmente retreina o modelo.
        
        Args:
            text (str): Texto do exemplo
            label (str): Rótulo da classe
            train_now (bool): Se True, retreina o modelo imediatamente
            
        Returns:
            bool: True se adicionado com sucesso, False caso contrário
        """
        try:
            # Obter exemplos existentes ou inicializar novos
            examples_file = os.path.join(os.path.dirname(self.model_file), 'training_examples.pkl')
            
            if os.path.exists(examples_file):
                with open(examples_file, 'rb') as f:
                    examples = pickle.load(f)
            else:
                examples = {'texts': [], 'labels': []}
            
            # Adicionar novo exemplo
            examples['texts'].append(text)
            examples['labels'].append(label)
            
            # Salvar exemplos
            os.makedirs(os.path.dirname(examples_file), exist_ok=True)
            with open(examples_file, 'wb') as f:
                pickle.dump(examples, f)
            
            logger.info(f"Exemplo de treinamento adicionado para a classe '{label}'")
            
            # Retreinar o modelo, se solicitado
            if train_now:
                return self.train(examples['texts'], examples['labels']) > 0.0
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar exemplo de treinamento: {str(e)}")
            return False 