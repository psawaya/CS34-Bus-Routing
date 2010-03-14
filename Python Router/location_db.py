from geopy import geocoders

import time

import sqlite3

#ABQIAAAAxvUcjYHQiRMj8NOewtBaKBStu2RGdso2Ia6oOTd8yAAQNqw8yRSdLY27dctGySnJTIxAaiJyWK9zDQ

class LocationDB:
    def __init__(self):
        self.conn = sqlite3.connect('locations')
        
        self.next_id = 1
        
        self.wait_secs = 1
        self.hadSuccess=True
        
        self.sleep_interval = 1
    
    def createTable(self):
        c = self.conn.cursor()
        
        # Create table
        c.execute("create table if not exists locations (id integer primary key, address text, lat numeric, long numeric)")
        
        self.conn.commit()
        
        c.close()
        
    def addLocation(self,address,unique_id=None):
        
        if self.sleep_interval > 10:
            time.sleep(self.wait_secs)
            self.sleep_interval = 1
        
        if unique_id is None: unique_id = self.next_id
        
        try:
            g = geocoders.Google("ABQIAAAAxvUcjYHQiRMj8NOewtBaKBStu2RGdso2Ia6oOTd8yAAQNqw8yRSdLY27dctGySnJTIxAaiJyWK9zDQ")
            
            place, (lat,lng) = g.geocode(address)
            
            c = self.conn.cursor()
            
            print "address %s, (%.15f,%.15f)" % (address,lat,lng)
            c.execute("insert into locations (id,address,lat,long) values ('%s','%s',%.15f,%.15f)" % (unique_id,address,lat,lng))
            
            self.conn.commit()
            
            c.close()
            
            self.next_id += 1
            
            self.hadSuccess=True
            
            return True

        except geocoders.google.GQueryError:
            print "Could not geocode address %s!\n" % address
        
        except geocoders.google.GTooManyQueriesError:
            print "Hit the rate limit!"
            
            if self.hadSuccess:
                self.hadSuccess = False
            else:
                self.wait_secs *= 2
                
                print "Hit the rate limit again, raising limit to %i" % self.wait_secs
                
            return False
                
        except ValueError:
            
            output_file = open ("human_edit.txt",'a')
            output_file.write ("%s\n" % address)
            output_file.close()
            
            return True
            

            
        