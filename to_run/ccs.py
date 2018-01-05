import xml.etree.ElementTree as ET
import random


class CCS:

	def __init__(self):
		self.ccs_tree = ET.parse('/var/www/journalhub/flaskapp/to_run/ccs.xml')
		self.ccs_root = self.ccs_tree.getroot()
		self.rdf_xmlns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
		self.skos_xmlns = "http://www.w3.org/2004/02/skos/core#"
		
		self.prefLabelTag = "{%s}prefLabel" % self.skos_xmlns
		self.altLabelTag = "{%s}altLabel" % self.skos_xmlns
		self.broaderTag = "{%s}broader" % self.skos_xmlns
		self.resourceTag = "{%s}resource" % self.rdf_xmlns
		self.conceptTag = "{%s}Concept" % self.skos_xmlns

	def get_parent_concept_id(self, target_label):

		parent_concept_ids = []

		target_label = target_label.lower()

		for concept in self.ccs_root.findall(self.conceptTag):
			is_target_label = False

			name = concept.find(self.prefLabelTag).text.lower()

			if name == target_label:
				is_target_label = True
			else:
				# Check if alternate labels mean the same as our target label
				for alt_label in concept.findall(self.altLabelTag):
					if alt_label.text.lower() == target_label:
						is_target_label = True

			if is_target_label:
				for broader in concept.findall(self.broaderTag):
					parent_concept_id = broader.get(self.resourceTag)
					parent_concept_ids.append(parent_concept_id)

		return parent_concept_ids


	def get_all_siblings(self, target_label):

		all_siblings = []
		parent_concept_ids = self.get_parent_concept_id(target_label)

		for concept in self.ccs_root.findall(self.conceptTag):
			for broader in concept.findall(self.broaderTag):

				parent_concept_id = broader.get(self.resourceTag)

				if parent_concept_id in parent_concept_ids:
					name = concept.find(self.prefLabelTag).text.lower()
					all_siblings.append(name)

		return all_siblings


	def get_random_sibling(self, target_label):

		siblings = self.get_all_siblings(target_label)

		siblings.remove(target_label)

		return random.choice(siblings)


if __name__ == "__main__":

	# TESTING PURPOSE

	ccs = CCS()
	print ccs.get_random_sibling("phishing")