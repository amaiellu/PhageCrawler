'''
Created on Oct 29, 2018

@author: amschaef
'''
from lxml import html
import requests
import pandas as pd



class PHASTCrawler: 
    def __init__(self,starting_url,depth,microbe):
        self.starting_url=starting_url
        self.root_url=starting_url.rsplit('/',1)[0]
        self.depth=depth
        self.microbe=microbe
        self.bactlist=[]
        self.phagelist=[]   
    
    def crawl(self):
        self.get_bacteria_from_link(self.starting_url,self.microbe)
        for bact in self.bactlist:
            self.get_phage_links_from_bacteria(bact)
            self.get_summary_phages(bact)
            self.get_tail_phages(bact)  
        self.generateStats(self.phagelist)
        return

    def get_bacteria_from_link(self,link,microbe):
        soup=self.getSoup(link)
        bact_table=soup.find_all('table')[4]
        bacts=bact_table.find_all('tr')
        for bact in bacts:
            if microbe in bact.get_text():
                tds=bact.find_all('td')
                phagenumber=tds[3].get_text()
                if phagenumber != '0':
                    name=tds[0].get_text()
                    phagelink=bact.find('a').get('href')
                    phagelink=self.root_url+phagelink
                    self.bactlist.append(Bacteria(name,phagelink))        
                
        return
    
    
    
    def get_tail_phages(self,bacteria):

        return
    
    

        
      
    def get_summary_phages(self,bacteria):
        
        return
    
    
    
    def generateStats(self,phagelist):
        
        return
    
class Bacteria:
    
        
    

class TailPhage:
   
        