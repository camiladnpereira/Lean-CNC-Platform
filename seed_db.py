import sqlite3
import random
from datetime import datetime, timedelta

def create_and_seed_db():
    conn = sqlite3.connect('usinagem.db')
    cursor = conn.cursor()

    # Criar tabela de eventos de produção
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS producao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            maquina TEXT,
            tempo_setup REAL,
            lead_time REAL,
            tempo_ciclo REAL,
            wip INTEGER,
            pecas_boas INTEGER,
            pecas_totais INTEGER,
            tempo_ativo REAL,
            tempo_total REAL
        )
    ''')
    # Gerar dados simulados para as 8 CNCs
    maquinas = [f"CNC-{i:02d}" for i in range(1, 9)]
    now = datetime.now()


    # Inserir registros históricos das últimas 24 horas para ter volume de dados
    for h in range(24, 0, -1):
        for maq in maquinas:
            ts = (now - timedelta(hours=h, minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
            tempo_ciclo = random.uniform(2.5, 5.0)  # minutos por peça
            pecas_totais = random.randint(10, 20)
            pecas_boas = pecas_totais - random.choice([0, 0, 0, 1])  # poucas perdas

            tempo_ativo = pecas_totais * tempo_ciclo
            tempo_total = tempo_ativo + random.uniform(10, 30)  # ativo + setups/paradas

            cursor.execute('''
                INSERT INTO producao (timestamp, maquina, tempo_setup, lead_time, tempo_ciclo, wip, pecas_boas, pecas_totais, tempo_ativo, tempo_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',(
                ts,
                maq,
                random.uniform(15, 45),  # Tempo de Setup (min)
                random.uniform(120, 300),  # Lead Time (min)
                tempo_ciclo,  # Tempo de Ciclo (min)
                random.randint(5, 25),  # WIP (Peças em processo)
                pecas_boas,
                pecas_totais,
                tempo_ativo,
                tempo_total
            ))

    conn.commit()
    conn.close()
    print("Banco de dados criado e populado com sucesso!")

if __name__ == "__main__":
    create_and_seed_db()

