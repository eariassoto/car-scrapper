from sys import stdout

class CarRecord(object):
    _id = 0
    title = ''
    link = ''
    attributes = {}
    equipment = []
    images = []

    def __init__(self, id, title, link, attributes, equipment, images):
      self._id = id
      self.link = link
      self.title = title
      self.attributes = attributes
      self.equipment = equipment
      self.images = images

    def Print(self):
      stdout.write('Title: ' + self.title)
      stdout.write('Id: ' + str(self.id))
      stdout.write('Link: ' + self.link)
      stdout.write('Attributes: ' + str(self.attributes))
      stdout.write('Equipment: ' + str(self.equipment))
      stdout.write('Images: ' + str(self.images))
