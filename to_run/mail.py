import smtplib
import urllib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mail:

    def __init__(self, from_email, to_email, password, papers, smtp_host):
        self.from_email = from_email
        self.to_email = to_email
        self.password = password
        self.papers = papers
        self.smtp_host = smtp_host


    def generate_html_message(self, papers):

        def build_links(papers):
            links = ""
            url = "http://journalhub.pragadeesh.com/"
            #TODO VERIFY LINK

            for paper in papers:
                paper_link = url + self.to_email + '/' + paper['title']
                
                like_base_link = url + "like?"
                dislike_base_link = url + "dislike?"
                parameters = urllib.urlencode({'userid': self.to_email,
                                               'paperid': paper['title']})

                like_link = like_base_link + parameters
                dislike_link = dislike_base_link + parameters

                links = links + """<a href='{}'>{}</a> <br/>
                <i><a href='{}'>Like</a> 
                <a href='{}'>Dislike</a> </i> <br/> <br/>
                """.format(paper_link, 
                        paper['title'],
                        like_link,
                        dislike_link)

            return links

        message = """<html>
                        <body>
                        <h3> Hello from journalhub! Here are your weekly recommendations: </h3>                        
                        {}
                        </body>
                    </html>""".format(build_links(papers))

        return message


    def send(self):
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Recommendations from journalhub"
        msg['From'] = self.from_email
        msg['To'] = self.to_email

        text = " "
        html = self.generate_html_message(self.papers)

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(self.from_email, self.password)
        server.sendmail(self.from_email, self.to_email, msg.as_string())
        server.close()


if __name__ == "__main__":

    papers = [{'title': "test paper"}]

    mail = Mail(from_email='journalhub.amrita@gmail.com',
                to_email="cpragadeesh@gmail.com",                    
                password="avvp#4321",
                papers=papers,
                smtp_host='smtp.gmail.com')

    print "Sending email..."
    mail.send()
    print "Email sent."