#!/usr/bin/python3
# Install the packages mentioned in the requirements.txt
# The program currently supports uploading files/directories to remote system using SCP.
# Support for downloading remote files/directories using SCP will be added in the upcoming version.


__Author__ = "Rajesh Kumar N"
__version__ = "0.1"


import os
import paramiko
from scp import SCPClient, SCPException
import socket
import sys
from time import sleep


class SSHTransferError(Exception):
	print("Error occurred while transferring files.")
	

class SCPConnection:
	def __init__(self, server, user, password=None, port=None):
		self.client = paramiko.SSHClient()
		self.load_client_defualt_settings()
		self.scp = None

		self.server = server
		self.user = user
		self.password = password
		self.port = port if port is not None else 22

	def load_client_defualt_settings(self):
		self.client.load_system_host_keys()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	def ssh_login(self):
		try:
			if self.password:
				self.client.connect(self.server, self.port, self.user, self.password, timeout=3)
			else:
				self.client.connect(self.server, self.port, self.user)
			return True
		except paramiko.ssh_exception.AuthenticationException as e:
			print("Login Failed.")
			print(e)
			return False
		except socket.timeout:
			print("SSH/SCP Server IP is unreachable.")
			sys.exit(1)

	def configure_scp_client(self):
		try:
			self.scp = SCPClient(self.client.get_transport())
			return True
		except (AttributeError, OSError):
			print("Kindly login to SSH first.")
			return False

	def transfer_input_files(self, *args, dst_path):
		try:		
			self.scp.put(args, remote_path=dst_path)
			print("Transferred {0} files successfully.".format(args))
			return True
		except AttributeError:
			print("Reconnecting on Connection Error")
			if not self.ssh_login():
				raise SSHTransferError
			self.configure_scp_client()
			return self.transfer_input_files(*args, dst_path=dst_path)
			
		except FileNotFoundError as e:
			print("Source file(s) path is/are invalid.")
			print(e)
		except SCPException:
			print("Destination path: {0} is inavlid.".format(dst_path))

	def transfer_input_dir(self, src_dir, dst_path):
		if os.path.isdir(src_dir):
			try:
				self.scp.put(src_dir, recursive=True, remote_path=dst_path)
				print("Transferred {0} directory successfully.".format(src_dir))
				return True
			except SCPException:
				print("Destination path: {0} is inavlid.".format(dst_path))
			except AttributeError:
				print("Reconnecting on Connection Error")
				if not self.ssh_login():
					raise SSHTransferError
				self.configure_scp_client()
				return self.transfer_input_dir(src_dir, dst_path=dst_path)
		else:
			print("Source directory - {0} is invalid.".format(src_dir))

	def close_connections(self):
		try:
			self.scp.close()
			self.client.close()
		except:
			print("No conenction exists to terminate.")


if __name__ == "__main__":
	scp_obj = SCPConnection(server="10.0.0.1", user="user", password="password")	
	scp_obj.ssh_login()
	scp_obj.configure_scp_client()
	# To transfer a file
	scp_obj.transfer_input_files('upload_file.txt', dst_path='~/upload_file.txt')
	# To trasnfer a directory
	scp_obj.transfer_input_dir('upload_dir', '~/')	
	scp_obj.close_connections()
