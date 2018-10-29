from lxml import html
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from collections import Counter



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
    
    def getSoup(self,link):
        start=requests.get(link)
        tree=html.fromstring(start.text)
        soup=BeautifulSoup(html.tostring(tree))
        
        return soup
    
    def get_phage_links_from_bacteria(self,bacteria):
        soup=self.getSoup(bacteria.phagelink)
        linkstable=soup.find_all('table')[1]
        links=linkstable.find_all('a')
        for link in links:
            if 'Summary' in link.get_text():
                bacteria.summaryLink=self.root_url+link.get('href')
            if 'Detailed' in link.get_text():
                bacteria.detailLink=self.root_url+link.get('href')
            
     
        return
    
    def get_summary_phages(self,bacteria):
        soup=self.getSoup(bacteria.summaryLink)
        phage_list=[]
        phagetable=soup.find_all('table')[0]
        rows=phagetable.find_all('tr')
        for row in rows: 
            if row.find_all('td') != []:
                phage_list.append(row.find_all('td')[6].get_text())
        
        bacteria.summaryPhage=phage_list
        
        return
    
    def get_tail_phages(self,bacteria):
        soup=self.getSoup(bacteria.detailLink)
        phagetables=soup.find_all('table')[1:]
        for table in phagetables:
            rows=table.find_all('tr')
            for row in rows:
                if 'tail' in row.get_text():
                    tds=row.find_all('td')
                    info=tds[2].get_text().split(':')
                    name=info[0]
                    proteintag=info[1].split(';')[0]
                    sequenceLink=self.root_url+tds[4].find('a').get('href')
                    sequence=self.getSoup(sequenceLink).get_text()
                    sequence= ''.join([i for i in sequence if i not in '[>.|0123456789]']) 
                    currentphages=self.phagelist
                    existingphage=next((phage for phage in currentphages if phage.name == name), False)
                    bacteria.tailPhages.append(name)
                    if existingphage:
                        newSequence=Sequence(sequence,proteintag,bacteria.name)
                        existingphage.sequences.append(newSequence)
                        if bacteria.name not in existingphage.bactList:
                            existingphage.bactList.append(bacteria.name)
                            
                        
                    else:
                        newPhage=TailPhage(name)
                        newPhage.sequenceLink=sequenceLink
                        newSequence=Sequence(sequence,proteintag,bacteria.name)
                        newPhage.sequences.append(newSequence)
                        newPhage.bactList.append(bacteria.name)
                        self.phagelist.append(newPhage)
                        
        
        return
    
    
    def generateStats(self,phagelist):
        # what stats do I need?
        # for each phage, number of bacteria detected
        phagenames=[phage.name for phage in phagelist]
        allproteinsheet=pd.DataFrame(index=np.arange(0,len(phagenames)),columns=['Name','Bacteria List'])
        allproteinsheet['Name']=pd.Series(phagenames)
       
        
        for phage in phagelist:
            name=phage.name
            bactlist=phage.bactList
            globalcount=len(bactlist.unique())
            sequences=phage.sequences
            phagesequencesheet=pd.DataFrame(index=np.arange(0,len(sequences)), columns=['Protein','Bacteria','Sequence'])
            proteintags=[sequence.proteintag for sequence in sequences]
            counts=Counter(proteintags).values()
            
            for sequence in sequences: 
                proteintags.append(sequence.proteintag)
                
            
        # for each phage, number of bacteria for each particular 'keyword' 
        # one sheet to list each sequence under specific prtein tag
        # 
        
        return
      
class Bacteria:
    def __init__(self, name, phagelink):
        self.name=name
        self.phagelink=phagelink
        self.summaryPhage=[]
        self.summaryLink=''
        self.detailLink=''
        self.tailPhages=[]
        
    

class TailPhage:
    def __init__(self,name): 
        self.name=name
        self.sequences=[]
        self.bactList=[]
        
class Sequence:
    def __init__(self,sequence,type,bacteria): 
        self.sequence=sequence
        self.type=type
        self.bacteria=bacteria
    
    
crawler=PHASTCrawler('http://phast.wishartlab.com/Download.html',0,'Bacteroides')
crawler.crawl()