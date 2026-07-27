"""Форматирование и отправка заявок по email."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from orders.order import Order
from .table_formatter import format_order_as_html_table, format_order_as_csv
from .text_formatter import format_order_as_text


class EmailFormatter:
    """Класс для форматирования и отправки заявок по email."""
    
    def __init__(self, smtp_host: str = None, smtp_port: int = 587, 
                 sender_email: str = None, sender_password: str = None):
        """
        Inicializacija parametrov email.
        
        Args:
            smtp_host: SMTP server (naprimer, smtp.gmail.com)
            smtp_port: Port SMTP
            sender_email: Email otsravitelya
            sender_password: Parol' otsravitelya
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def create_message(self, order: Order, recipient_email: str, 
                      format_type: str = 'html', subject: str = None) -> MIMEMultipart:
        """
        Создает email сообщение с заявкой.
        
        Args:
            order: Объект заявки
            recipient_email: Email получателя
            format_type: Формат содержимого ('html', 'text', 'both')
            subject: Тема письма
            
        Returns:
            Объект MIMEMultipart сообщения
        """
        if subject is None:
            subject = f"Заявка на продукцию №{order.order_id}"
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = self.sender_email
        message['To'] = recipient_email
        
        # Текстовая версия
        text_content = format_order_as_text(order)
        part_text = MIMEText(text_content, 'plain', 'utf-8')
        message.attach(part_text)
        
        # HTML версия
        if format_type in ('html', 'both'):
            html_content = format_order_as_html_table(order)
            part_html = MIMEText(html_content, 'html', 'utf-8')
            message.attach(part_html)
        
        return message
    
    def send_email(self, order: Order, recipient_email: str = None, 
                  format_type: str = 'html', subject: str = None) -> bool:
        """
        Отправляет заявку по email.
        
        Args:
            order: Объект заявки
            recipient_email: Email получателя (если None, используется email из заявки)
            format_type: Формат содержимого
            subject: Тема письма
            
        Returns:
            True если успешно отправлено, False если ошибка
        """
        if not self.sender_email or not self.sender_password:
            print("Ошибка: не установлены параметры для отправки email")
            return False
        
        if recipient_email is None:
            recipient_email = order.customer_email
        
        try:
            message = self.create_message(order, recipient_email, format_type, subject)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print("[OK] Email uspeshno otpravlen na " + recipient_email)
            return True
            
        except Exception as e:
            print("[ERROR] Oshibka pri otpravke email: " + str(e))
            return False
    
    def export_to_files(self, order: Order, output_dir: str = './exports') -> dict:
        """
        Eksportiruet zayavku vo vse formaty v fajly.
        
        Args:
            order: Ob'ekt zayavki
            output_dir: Direktoria dlya sohraneniya fajlov
            
        Returns:
            Slovar' s putyami k sohranennym fajlam
        """
        from .text_formatter import save_text_to_file
        from .table_formatter import save_csv_to_file, save_html_to_file
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        base_name = f"{order.order_id}"
        
        files = {
            'text': save_text_to_file(
                order, 
                str(output_path / f"{base_name}.txt")
            ),
            'csv': save_csv_to_file(
                order,
                str(output_path / f"{base_name}.csv")
            ),
            'html': save_html_to_file(
                order,
                str(output_path / f"{base_name}.html")
            ),
        }
        
        print("[OK] Zayavka eksportirana v " + str(len(files)) + " fajlov")
        for fmt, path in files.items():
            print("  - " + fmt.upper() + ": " + path)
        
        return files
